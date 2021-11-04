from pydantic import BaseModel

STATUS400_DESC = 'Bad Request.'
STATUS401_DESC = 'Invalid access token / Invalid username or password.'
STATUS403_DESC = 'Required admin token to access this route.'
STATUS404_DESC = 'Request resourses can not found in the server.'
STATUS413_DESC = 'Request entity too small/large.'
STATUS415_DESC = 'Unsupported media types'

class Status400(BaseModel):
    detail: str
    class Config:
        schema_extra ={
            'example': {
                'detail': 'Duplicated Email.'
            }
        }

class Status401(BaseModel):
    detail: str
    class Config:
        schema_extra ={
            'example': {
                'detail': 'Invalid token or expired token.'
            }
        }

class Status403(BaseModel):
    detail: str
    class Config:
        schema_extra ={
            'example': {
                'detail': 'Not enough privileges.'
            }
        }

class Status404(BaseModel):
    detail: str
    class Config:
        schema_extra ={
            'example': {
                'detail': 'User not found.'
            }
        }
