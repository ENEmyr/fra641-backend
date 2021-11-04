from pydantic import BaseModel

class HTTPExceptionRes(BaseModel):
    detail: str
    class Config:
        schema_extra ={
            'example': {
                'detail': 'some detail about exception.'
            }
        }
