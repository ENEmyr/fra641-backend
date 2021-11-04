from random import choice, seed
from string import ascii_letters, digits, punctuation
from time import time
from typing import List, Optional

from Crypto.Hash import SHA512
from databases import Database
from fastapi import Depends, FastAPI, HTTPException

import models.responses
from helpers.generate_responses_dict import gen_res_dict
from helpers.auth_bearer import JWTBearer
from helpers.auth_handler import decode_token, sign_token
from models import User, UserId, UserInfo, UserInfoPwd, UserRegis, UserSignin

# 3600 = 1 Hr
TOKEN_DURATION = 3600*24

def export_routes(route:str, router:FastAPI, db:Database):
    @router.post(
        route+'/register',
        status_code=201,
        tags=[route[1:], 'no_tokens_required'],
        responses={
            **gen_res_dict(status_codes=[400]),
            201: {
                'description': 'User Created.',
                'content': {
                    'application/json': {
                        'example': {
                            'UserId': 1
                        }
                    }
                }
            }
        }
    )
    async def register(user_regis: UserRegis):
        seed(int(time())) # gen new random seed from current unix time
        salt = ''.join(choice(ascii_letters+digits+punctuation) for _ in range(50))
        hash = SHA512.new((user_regis.password+salt).encode('ascii'))
        user_regis.password = hash.hexdigest()
        user = User(
            **user_regis.dict(),
            password_salt=salt
        )
        user_dict = user.dict()
        del user_dict['user_id']
        check_duplicate_query = "SELECT email from `user` WHERE email = :email"
        dup_res = await db.fetch_one(query=check_duplicate_query, values={'email': user.email})
        if dup_res is None:
            regis_query = "INSERT INTO `user`({}) VALUES \
                ({})".format(
                    ','.join(user_dict.keys()),
                    ','.join([':'+x for x in user_dict.keys()])
                )
            regis_res = await db.execute(query=regis_query, values=user_dict)
            return {'UserId': str(regis_res)}
        else:
            return HTTPException(status_code=400, detail='Duplicated Email.')

    @router.post(
        route+'/signin',
        tags=[route[1:], 'no_tokens_required'],
        responses={
            **gen_res_dict(status_codes=[401]),
            200:{
                'description':'Return access token and token type.',
                'content': {
                    'application/json': {
                        'example': {
                            'access_token':'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo2LCJyb2xlIjp0cnVlLCJleHAiOjE2MTU3NTczMDkuNDI2NTMwNH0.FARjxsN4Z3wU7u7DhYP3BJn_E1y0y25c9-w1FZNSuks',
                            'token_type':'bearer'
                        }
                    }
                }
            }
        }
    )
    async def signin(signin_item:UserSignin):
        lookup_query = "SELECT user_id, role, password, password_salt FROM `user` WHERE email = :email"
        lookup_res = await db.fetch_one(query=lookup_query, values={'email': signin_item.email})
        if lookup_res is not None:
            (user_id, role, pwd, pwd_salt) = lookup_res
            hashed_pwd = SHA512.new((signin_item.password+pwd_salt).encode('ascii')).hexdigest()
            if hashed_pwd == pwd:
                token = sign_token(
                    user_id=user_id,
                    role=True if role == '1' else False,
                    exp=time()+TOKEN_DURATION
                )
                # need to collect login log
                return token
            else:
                return HTTPException(status_code=401, detail='Password mismatch.')
        else:
            return HTTPException(status_code=401, detail='User not found.')

    @router.get(
        route+'/query',
        tags=[route[1:], 'admin_token'],
        responses={
            **gen_res_dict(status_codes=[400, 401, 403]),
            200:{
                'description':'Return list of queried users data.',
                'model': List[UserInfo]
            }
        }
    )
    async def query_user_data(
        token: str = Depends(JWTBearer(verify_admin=True)),
        offset: int = 1,
        limit: int = 1,
        id: Optional[UserId] = None):
        # need to collect query log
        if id is not None:
            try:
                lookup_query = "SELECT {} FROM `user` WHERE user_id = :user_id".format(','.join(UserInfo.__fields__.keys()))
                lookup_res = await db.fetch_one(query=lookup_query, values={'user_id': id})
            except:
                raise HTTPException(status_code=500, detail='Something went wrong when trying to query a request.')
            else:
                if lookup_res == None:
                    return {}
                res_dict = dict(zip(UserInfo.__fields__.keys(), lookup_res))
                info = UserInfo(**res_dict)
                return [info.dict()]
        else:
            try:
                lookup_query = "SELECT {} FROM `user` WHERE user_id >= :offset LIMIT :limit".format(','.join(UserInfo.__fields__.keys()))
                lookup_res = await db.fetch_all(query=lookup_query, values={'offset': offset, 'limit': limit})
            except:
                raise HTTPException(status_code=500, detail='Something went wrong when trying to query a request.')
            else:
                if lookup_res == None:
                    return {}
                infos = [UserInfo(**dict(zip(UserInfo.__fields__.keys(), x))) for x in lookup_res]
                return infos

    @router.put(
        route,
        tags=[route[1:], 'user_token'],
        responses={
            **gen_res_dict(status_codes=[500]),
            200: {
                'description': 'Operation result.',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True
                        }
                    }
                }
            }
        }
    )
    async def update_info(
        user_info_pwd: UserInfoPwd,
        token: str = Depends(JWTBearer())):
        decoded = decode_token(token)
        # need to collect update log
        if user_info_pwd.password != None:
            seed(time())
            salt_query = "SELECT password_salt FROM `user` WHERE user_id = :user_id"
            salt_res = await db.fetch_one(salt_query, values={'user_id': decoded['user_id']})
            hash = SHA512.new((user_info_pwd.password+salt_res[0]).encode('ascii'))
            user_info_pwd.password = hash.hexdigest()
        user_dict = {}
        for key, val in zip(user_info_pwd.dict().keys(), user_info_pwd.dict().values()):
            if key == 'role':
                # Ordinary user have no right to update own role
                continue
            if val != None and val != '':
                user_dict[key] = val
        if len(user_dict) == 0:
            return {'success': False}
        user_dict['user_id'] = decoded['user_id']
        update_query = "UPDATE `user` SET {} WHERE user_id = :user_id".format(
            ','.join(x+' = :'+x for x in list(user_dict.keys()))
        )
        update_res = await db.execute(update_query, values=user_dict)
        return {'success': True} if update_res == 1 else {'success': False}

    @router.put(
        route+'/alter',
        tags=[route[1:], 'admin_token'],
        responses={
            **gen_res_dict(status_codes=[500]),
            200: {
                'description': 'Operation result.',
                'content': {
                    'application/json': {
                        'example': {
                            'success': True
                        }
                    }
                }
            }
        }
    )
    async def alter_user_info(user_info: UserInfo, token: str = Depends(JWTBearer(verify_admin=True))):
        # need to collect alter log
        if user_info.user_id == None or user_info.user_id == '':
            return {'success': False}
        user_dict = {}
        for key, val in zip(user_info.dict().keys(), user_info.dict().values()):
            if val != None and val != '':
                user_dict[key] = val
        if len(user_dict) == 0:
            return {'success': False}
        update_query = "UPDATE `user` SET {} WHERE user_id = :user_id".format(
            ','.join(x+' = :'+x for x in list(user_dict.keys()))
        )
        update_res = await db.execute(update_query, values=user_dict)
        return {'success': True} if update_res == 1 else {'success': False}

    @router.delete(
        route+'/{user_id}',
        tags=[route[1:], 'admin_token'],
        responses={
            **gen_res_dict(status_codes=[500]),
            200: {
                'description': 'Operation result.',
                'content': {
                    'application/json': {
                        'example': {
                            'deleted_user_id': 'user_id not found'
                        }
                    }
                }
            }
        }
    )
    async def delete_user(user_id: UserId, token: str = Depends(JWTBearer(verify_admin=True))):
        # need to collect delete log
        query = "DELETE FROM `user` WHERE user_id = :user_id"
        res = await db.execute(query=query, values={'user_id': user_id})
        return {'deleted_user_id': user_id if res == 1 else 'user_id not found.'}

    @router.get(
        route,
        tags=[route[1:], 'user_token'],
        responses={
            **gen_res_dict(status_codes=[404, 500]),
            200: {
                'description': 'Returned user data.',
                'model': UserInfo
            }
        }
    )
    async def get_user_data(token: str = Depends(JWTBearer())):
        decoded = decode_token(token)
        # need to collect get_data log
        try:
            data_query = 'SELECT {} FROM `user` WHERE user_id = :user_id'.format(','.join(UserInfo.__fields__.keys()))
            data_res = await db.fetch_one(data_query, values={'user_id': decoded['user_id']})
            if len(data_res) !=  0:
                data_dict = dict(zip(UserInfo.__fields__.keys(), data_res))
                user_info = UserInfo(**data_dict)
                return user_info
            else:
                return HTTPException(status_code=404, detail='User not found.')
        except Exception as e:
            return HTTPException(status_code=500, detail=f'Error: {e}')
