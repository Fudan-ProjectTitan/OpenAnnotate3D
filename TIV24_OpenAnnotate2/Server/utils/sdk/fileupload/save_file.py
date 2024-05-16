import json
import math
import os
import time
from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
import hashlib
import base64
import hmac
from urllib.parse import urlparse
import requests
from urllib3 import encode_multipart_formdata

lfasr_host = 'http://upload-ost-api.xfyun.cn/file'
# 请求的接口名
api_init = '/mpupload/init'
api_upload = '/upload'
api_cut = '/mpupload/upload'
api_cut_complete = '/mpupload/complete'
api_cut_cancel = '/mpupload/cancel'
# 文件分片大小5M
file_piece_sice = 5242880


# 文件上传
class SeveFile:
    def __init__(self, app_id, api_key, api_secret,upload_file_path):
        self.app_id = app_id
        self.api_key = api_key
        self.api_secret = api_secret
        self.request_id = '0'
        self.upload_file_path = upload_file_path
        self.cloud_id = '0'

    # request_id处理
    def get_request_id(self):
        return time.strftime("%Y%m%d%H%M")

    # header处理
    def hashlib_256(self, data):
        m = hashlib.sha256(bytes(data.encode(encoding='utf-8'))).digest()
        digest = "SHA-256=" + base64.b64encode(m).decode(encoding='utf-8')
        return digest

    # header处理
    def assemble_auth_header(self, requset_url, file_data_type, method="", api_key="", api_secret="", body=""):
        u = urlparse(requset_url)
        host = u.hostname
        path = u.path
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        digest = "SHA256=" + self.hashlib_256('')
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1\ndigest: {}".format(host, date, method, path, digest)
        signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            api_key, "hmac-sha256", "host date request-line digest", signature_sha)
        headers = {
            "host": host,
            "date": date,
            "authorization": authorization,
            "digest": digest,
            'content-type': file_data_type,
        }
        return headers

    # post请求api
    def call(self,  url, file_data, file_data_type):
        api_key = self.api_key
        api_secret = self.api_secret
        headerss = self.assemble_auth_header(url, file_data_type, method="POST",
                                             api_key= api_key,api_secret = api_secret, body = file_data)
        try:
            resp = requests.post(url, headers=headerss, data=file_data, timeout=8)
            # print("该片上传成功.状态：",resp.status_code, resp.text)
            return resp.json()
        except Exception as e:
            print("该片上传失败！Exception ：%s" % e)
            return False


    # 分块上传完成
    def upload_cut_complete(self, body_dict):
        file_data_type = 'application/json'
        url = lfasr_host + api_cut_complete
        fileurl = self.call(url, json.dumps(body_dict), file_data_type)
        fileurl = fileurl['data']['url']
        print("任务上传结束")
        return fileurl

    # 根据不同的apiname生成不同的参数,本示例中未使用全部参数您可在官网(https://aidocs.xfyun.cn/docs/ost/%E5%A4%9A%E7%A7%9F%E6%88%B7%E6%96%87%E4%BB%B6%E4%B8%8A%E4%BC%A0%E6%8E%A5%E5%8F%A3%E6%96%87%E6%A1%A3.html)查看后选择适合业务场景的进行更换
    def gene_params(self, apiname):
        appid = self.app_id
        request_id = self.get_request_id()
        upload_file_path = self.upload_file_path
        cloud_id = self.cloud_id
        body_dict = {}
        # 上传文件api
        if apiname == api_upload:
            try:
                with open(upload_file_path, mode='rb') as f:
                    file = {
                        "data": (upload_file_path, f.read()),
                        "app_id": appid,
                        "request_id": request_id,
                    }
                    print('文件：', upload_file_path, ' 文件大小：', os.path.getsize(upload_file_path))
                    encode_data = encode_multipart_formdata(file)
                    #print("----",encode_data)
                    file_data = encode_data[0]
                    file_data_type = encode_data[1]
                url = lfasr_host + api_upload
                fileurl = self.call(url, file_data, file_data_type)
                #print("文件上传参数",file_data)
                return fileurl
            except FileNotFoundError:  # 文件不能找到的异常处理
                print("Sorry!The file " + upload_file_path + " can't find.")
            # 预处理api
        elif apiname == api_init:
            body_dict['app_id'] = appid
            body_dict['request_id'] = request_id
            body_dict['cloud_id'] = cloud_id
            url = lfasr_host + api_init
            file_data_type = 'application/json'
            return self.call(url, json.dumps(body_dict), file_data_type)
        elif apiname == api_cut:
            # 预处理
            upload_prepare = self.prepare_request()
            if upload_prepare:
                upload_id = upload_prepare['data']['upload_id']
            # 分块上传
            self.do_upload(upload_file_path, upload_id)
            body_dict['app_id'] = appid
            body_dict['request_id'] = request_id
            body_dict['upload_id'] = upload_id
            # 分块上传完成
            fileurl = self.upload_cut_complete(body_dict)
            print("分片上传地址：",fileurl)
            return fileurl



    # 预处理
    def prepare_request(self):
        return self.gene_params(apiname=api_init)


    # 分片上传
    def do_upload(self, file_path, upload_id):
        file_total_size = os.path.getsize(file_path)
        chunk_size = file_piece_sice
        chunks = math.ceil(file_total_size / chunk_size)
        appid = self.app_id
        request_id = self.get_request_id()
        upload_file_path = self.upload_file_path
        slice_id = 1

        print('文件：', file_path, ' 文件大小：', file_total_size, ' 分块大小：', chunk_size, ' 分块数：', chunks)

        with open(file_path, mode='rb') as content:
            while slice_id <= chunks:
                print('chunk',slice_id )
                if (slice_id-1) + 1 == chunks:
                    current_size = file_total_size % chunk_size
                else:
                    current_size = chunk_size

                file = {
                    "data": (upload_file_path, content.read(current_size)),
                    "app_id": appid,
                    "request_id": request_id,
                    "upload_id": upload_id,
                    "slice_id": slice_id,
                }

                encode_data = encode_multipart_formdata(file)
                file_data = encode_data[0]
                file_data_type = encode_data[1]
                url = lfasr_host + api_cut

                resp = self.call(url, file_data, file_data_type)
                count = 0
                while not resp and (count<3):
                    print("上传重试")
                    resp = self.call(url, file_data, file_data_type)
                    count = count + 1
                    time.sleep(1)
                if not resp:
                    quit()
                slice_id = slice_id + 1
