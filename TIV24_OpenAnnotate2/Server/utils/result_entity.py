class ResultEntity():
    def __init__(self, code = None, message = None, data = None):
        self.code = code
        self.message = message
        self.data = data
        
    def result(self):
        return {"code": self.code, "message": self.message, "data": self.data}