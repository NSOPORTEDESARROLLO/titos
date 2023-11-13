import urllib.request
import filetype
from datetime import datetime
import random
from pathlib import Path
import base64
import shutil

class WorkWithFile():
    __filename = ""
    
    def get_file_name(self)->dict:
        # it returns random path/filename
        data = {}
        dt = datetime.now()
        ran = random.randrange(123456-78905464,4)
        data['dir'] = f"/tmp/titos/base64/{dt.strftime('%d')}/{dt.strftime('%m')}/{dt.strftime('%Y')}_{dt.strftime('%H')}-{dt.strftime('%M')}-{dt.strftime('%S')}"
        data['filename'] = ran
        data['fullpath'] = f"/tmp/titos/base64/{dt.strftime('%d')}/{dt.strftime('%m')}/{dt.strftime('%Y')}_{dt.strftime('%H')}-{dt.strftime('%M')}-{dt.strftime('%S')}/{ran}"
        return data

    def get_file_from_url(self,url:str)->dict:
        '''
            download file and get its type
        '''
        data = {}
        imp = self.get_file_name()
        data['error'] = None
        data['url'] = url
        data['dir'] = imp['dir']
        data['filename'] = imp['fullpath']
        Path(data['dir']).mkdir(parents=True,exist_ok=True)
        
        try:
            urllib.request.urlretrieve(url,data['filename'])
            data['type'] = filetype.guess(data['filename']).mime
            data['base64'] = self.encode_base64(data['filename'])
            shutil.rmtree(data['dir'],)
        except:
            data['error_name'] = "NOT_MEDIA"
            data['error_message'] = "Please set arguments in request json body, not in params. Not a media message"
       
        #print(data)
        return data

    def encode_base64(self,file:str)->str:
        with open(file,"rb") as image_file:
            base64_string = base64.b64encode(image_file.read())
        return base64_string.decode("utf-8")

    def get_encode(self,url:str)->dict:
        data = self.get_file_from_url(url)
        #print (data)
        response = {}

        if data.get('error_name') is not None:
            response = {
                'success' : False, 
                'error' : { 'name' : data['error_name'], 'message': data['error_message']} 
            }
        else:
            response = {
                'success' : True,
                'response' : f"data:{data['type']};base64,{data['base64']}"
            }

        return response