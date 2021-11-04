from pydantic import BaseModel

STATUS500_DESC = 'Internal Server Errors'

class Status500(BaseModel):
    detail: str
    class Config:
        schema_extra ={
            'example': {
                'detail': 'error occur {e}'
            }
        }
