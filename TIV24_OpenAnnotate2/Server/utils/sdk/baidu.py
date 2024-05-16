import os
import base64
import time
import requests
import json

class BaiduCloud():
    def __init__(self):
        self.client_id = ""
        self.client_secret = ""
        self.cuid = ""
        
    def get_file_size(self, path):
        return os.path.getsize(path)
    
    def get_file_base64(self, path):
        with open(path, "rb") as wav_file:
            return base64.b64encode(wav_file.read()).decode("utf-8")
    
    def get_AccessToken(self):
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {"grant_type": "client_credentials", "client_id": self.client_id, "client_secret": self.client_secret}
        return str(requests.post(url, params=params).json().get("access_token"))
        
    def standard_speech(self, path):
        url = "https://vop.baidu.com/server_api"
         
        payload = json.dumps({
            "format": "wav",
            "rate": 16000,
            "channel": 1,
            "cuid": self.cuid,
            "token": self.get_AccessToken(),
            "speech": self.get_file_base64(path),
            "len": self.get_file_size(path)
        })
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        
        return json.loads(response.text)
    
    def short_speech(self, path):
        url = "https://vop.baidu.com/pro_api"
         
        payload = json.dumps({
            "format": "wav",
            "rate": 16000,
            "channel": 1,
            "cuid": self.cuid,
            "token": self.get_AccessToken(),
            "dev_pid": 80001,
            "speech": self.get_file_base64(path),
            "len": self.get_file_size(path)
        })
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        
        return json.loads(response.text)