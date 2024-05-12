#!/bin/bash

# Create conda environment
conda create -n openannotate3d-icra24 python=3.8
conda activate openannotate3d-icra24
conda install pytorch==2.2.2 torchvision==0.17.2 torchaudio==2.2.2 pytorch-cuda=11.8 -c pytorch -c nvidia
pip install git+https://github.com/IDEA-Research/GroundingDINO.git
pip install git+https://github.com/facebookresearch/segment-anything.git
pip install langchain
pip install openai==0.28
pip install openai-whisper
pip install flask
pip install chardet