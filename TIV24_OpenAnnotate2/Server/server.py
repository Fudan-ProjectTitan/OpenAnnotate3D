import os
import json
import torch
import multiprocessing
from flask import Flask, jsonify, request

from utils.result_entity import ResultEntity
from utils.agent import translate
from utils.process import process_image
from utils.sdk.baidu import BaiduCloud
from utils.whisper_model import speech_recognition
from utils.command import run as command_run

baidu_api = BaiduCloud()
root_dir = "logger/files"
app = Flask(__name__)
@app.route('/api/lc_history', methods=['POST'])
def lc_history():
    try:
        question = request.form.get("question")
        if question == "" or question is None:
            return jsonify(ResultEntity(500, "question is empty.").result())

        image = request.files.get("image_file")
        if image is None or image.filename == "":
            return jsonify(ResultEntity(500, "Missing image file.").result())

        image_dir = os.path.join(root_dir, "image")
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)

        threshold = request.form.get("threshold")
        if threshold is None or threshold == "":
            return jsonify(ResultEntity(500, "threshold field information is empty.").result())

        image_file = os.path.join(image_dir, image.filename)
        image.save(image_file)

        result = translate(question)
        res_json = json.loads(process_image(image_file, result, threshold))
        return jsonify(ResultEntity(200, "success.", {"text": result, "data": res_json}).result())
    except Exception as e:
        return jsonify(ResultEntity(500, str(e)).result())
    
@app.route('/api/get_audio', methods=['POST'])
def get_audio():
    try:
        id = request.form.get("id")
        if id is None or id == "":
            return jsonify(ResultEntity(500, "The id field information is empty.").result())

        audio = request.files.get("audio_file")
        if audio is None or audio.filename == "":
            return jsonify(ResultEntity(500, "Missing audio file.").result())

        audio_dir = os.path.join(root_dir, id, "audio")
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)

        audio_file = os.path.join(audio_dir, audio.filename)
        audio.save(audio_file)
        
        speech_text, speech_language = speech_recognition(audio_file)
        return jsonify(ResultEntity(200, "success.", {"speech_text": speech_text, "speech_language": speech_language}).result())
    except Exception as e:
        return jsonify(ResultEntity(500, str(e)).result())
    
@app.route('/api/command', methods=['POST'])
def command():
    try:
        environment = request.form.get("environment")
        if environment == "" or environment is None:
            return jsonify(ResultEntity(500, "environment is empty.").result())
        
        content = request.form.get("content")
        if content is None or content == "":
            return jsonify(ResultEntity(500, "content is empty.").result())
        
        result = translate(content)             
        result = command_run(environment, content)            
        return jsonify(ResultEntity(200, "success.", result).result())
    except Exception as e:
        return jsonify(ResultEntity(500, str(e)).result())

if __name__ == "__main__":
    try:      
        process = multiprocessing.Process(target=(app.run(host='0.0.0.0', port=5002)))
        process.start()
    except KeyboardInterrupt as e:
        print(e)