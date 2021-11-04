from pydantic import BaseModel

STATUS201_DESC = 'Created.'

class Status201(BaseModel):
    detail: str
    class Config:
        schema_extra ={
            'example': {
                'detail': 'User Created.'
            }
        }
