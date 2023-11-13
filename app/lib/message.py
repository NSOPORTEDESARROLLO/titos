from pydantic import BaseModel

class Message(BaseModel):

    message: str = "Check documentation in description"
    token: str

class Args(BaseModel):
   
    args: Message


