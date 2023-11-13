from fastapi import FastAPI
from lib.message import Message, Args
from lib.utils import WorkWithFile
from etc.config import get_app_token

app = FastAPI(title="Nsoporte Base64 encoder",
              description="Convert any media to base64")

@app.post('/decryptMedia')
async def encode(args:Args):
    '''
    Decrypts a media message.
    Parameter: message This can be the serialized [[MessageId]] or the whole [[Messag] object. It is advised to just use the serialized message ID.
    @returns Promise<[[DataURL]]>
    '''
    if args.args.token == get_app_token():

        url = args.args.message
        wwf = WorkWithFile()
        return wwf.get_encode(args.args.message)
    else:
        return {"error": "Invalid Token" }