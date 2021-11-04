from typing import NewType

from pydantic import BaseModel, Field, PositiveInt, root_validator, validator
from validators import email as validate_email

ID_LENGTH = 20
UserId = NewType('UserId', PositiveInt)

# REST Models
class UserInfo(BaseModel):
    user_id: UserId = Field(default=None)
    email: str = Field(default=None, max_length=300, description='User email.')
    first_name: str = Field(default=None, max_length=300)
    last_name: str = Field(default=None, max_length=300)
    role: bool = Field(default=None, description='If not defined role will be user(false) by default.') # 1 is admin, 0 is ordinary user

    @root_validator
    def root_validate(cls, values):
        if values.get('email') != None:
            if not validate_email(values.get('email')):
                raise ValueError('given email not in the email form.')
        return values
    class Config:
        schema_extra = {
            'example': {
                'user_id': 1,
                'email': 'test@admin.com',
                'first_name': 'Kevin',
                'role': True
            }
        }
class UserInfoPwd(UserInfo):
    password: str = Field(default=None, description='User password.')
    @validator("password")
    def check_len_pwd(cls, v):
        if v != None:
            if len(v) < 8:
                raise ValueError('password must longer than 8 characters')
        return v

class UserSignin(BaseModel):
    email: str = Field(..., max_length=300, description='User email.')
    password: str = Field(..., description='User password.')

    @validator('email')
    def validate_mail_form(cls, v):
        if not validate_email(v):
            raise ValueError('given email not in the email form.')
        return v
    @validator("password")
    def check_len_pwd(cls, v):
        if len(v) < 8:
            raise ValueError('password must longer than 8 characters')
        return v

class UserRegis(UserSignin):
    first_name: str = Field(..., max_length=300)
    last_name: str = Field(..., max_length=300)
    role: bool = Field(False, description='If not defined role will be user(false) by default.') # 1 is admin, 0 is ordinary user

    @root_validator
    def can_not_contain_space(cls, values):
        if ' ' in values.get('first_name') or ' ' in values.get('last_name'):
            raise ValueError('fist_name/last_name can\'t contains a space.')
        return values

# Database Model
class User(UserInfo):
    password: str = Field(default_factory=str, max_length=128, min_length=128, description='Hashing with SHA512 algorithm.')
    password_salt: str = Field(default_factory=str, max_length=50, min_length=50, description='Salt that add into password to compute hash, it\'t not required because it can be generated at backend.')

    @root_validator
    def root_validate(cls, values):
        if len(str(values.get('password'))) != 128:
            raise ValueError('Hashing password length not equal to 128(SHA512)')
        if len(str(values.get('password_salt'))) != 50:
            raise ValueError('length of password salt must equal to 50')
        return values

