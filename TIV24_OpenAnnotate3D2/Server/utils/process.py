import cv2
import json
import torch
import torchvision
from flask import jsonify

from GroundingDINO.groundingdino.util.inference import load_model, load_image, predict
from segment_anything import build_sam, SamPredictor

from utils.result_entity import ResultEntity

config_file = "GroundingDINO/groundingdino/config/GroundingDINO_SwinB_cfg.py"
grounded_checkpoint = "models/groundingdino_swinb_cogcoor.pth"
sam_checkpoint = "models/sam_vit_h_4b8939.pth"
device = "cuda"
box_threshold = 0.3

_model = load_model(config_file, grounded_checkpoint)
predictor = SamPredictor(build_sam(checkpoint=sam_checkpoint))

def get_grounding_output(model, image, caption, threshold):
    boxes, logits, phrases = predict(
        model=model, 
        image=image, 
        caption=caption, 
        box_threshold=box_threshold, 
        text_threshold=threshold
    )
    
    return boxes, logits, phrases

def process_image(image_file, text, threshold):
    try:        
        # load image
        image_pil, imageStream = load_image(image_file)
        
        # run grounding dino model
        boxes, logits, phrases = get_grounding_output(_model, imageStream, text, float(threshold))
        
        # initialize SAM
        _image = cv2.imread(image_file)
        _image = cv2.cvtColor(_image, cv2.COLOR_BGR2RGB)
        predictor.set_image(_image)

        H, W, _ = image_pil.shape
        for i in range(boxes.size(0)):
            boxes[i] = boxes[i] * torch.Tensor([W, H, W, H])
            boxes[i][:2] -= boxes[i][2:] / 2
            boxes[i][2:] += boxes[i][:2]
        
        if boxes.shape[0] == 0:
            return jsonify(ResultEntity(404, "success.").result())
        
        transformed_boxes = predictor.transform.apply_boxes_torch(boxes, _image.shape[:2])
        masks, _, _ = predictor.predict_torch(
            point_coords = None,
            point_labels = None,
            boxes = transformed_boxes,
            multimask_output = False,
        )
        
        value = 0
        mask_image = torch.zeros(masks.shape[-2:])
        for idx, mask in enumerate(masks):
            mask_image[mask.cpu().numpy()[0] == True] = value + idx + 1
            
        json_box = []
        for label, box in zip(phrases, boxes):
            name = label
            json_box.append({
                'label': name,
                'box': box.numpy().tolist(),
            })
                                           
        return json.dumps(ResultEntity(200, "success.", {"mask": mask_image.numpy().tolist(), "box": json_box}).result())
    except Exception as e:
        print(f"error: {str(e)}")
        return json.dumps(ResultEntity(500, str(e)).result())
    
def sam_image(image_file, boxes):
    try:
        # initialize SAM
        _image = cv2.imread(image_file)
        _image = cv2.cvtColor(_image, cv2.COLOR_BGR2RGB)
        predictor.set_image(_image)
        
        transformed_boxes = predictor.transform.apply_boxes_torch(boxes, _image.shape[:2])
        masks, _, _ = predictor.predict_torch(
            point_coords = None,
            point_labels = None,
            boxes = transformed_boxes,
            multimask_output = False,
        )
        
        value = 0
        mask_image = torch.zeros(masks.shape[-2:])
        for idx, mask in enumerate(masks):
            mask_image[mask.cpu().numpy()[0] == True] = value + idx + 1
        
        return json.dumps(ResultEntity(200, "success.", {"mask": mask_image.numpy().tolist()}).result())
    except Exception as e:
        print(f"error: {str(e)}")
        return json.dumps(ResultEntity(500, str(e)).result())