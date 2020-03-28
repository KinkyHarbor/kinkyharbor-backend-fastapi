'''This module contains all registration related routes'''

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, constr, EmailStr, Field, validator
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT

from harbor.domain.common import StrictBoolTrue, DisplayNameStr, StrongPasswordStr, Message
from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.auth import (
    register as uc_user_register,
    register_verify as uc_user_reg_verify,
)


router = APIRouter()


class FormRegister(BaseModel):
    '''Required form data for registering a user'''
    display_name: DisplayNameStr = Field(..., alias='username')
    email: EmailStr
    password: StrongPasswordStr = Field(...,
                                        description='Password should either be 16 characters or '
                                        'longer (passphrase). Or should be minimum 8 long and '
                                        'have lower case, upper case and a digit.')
    is_adult: StrictBoolTrue = Field(...,
                                     title='Is adult',
                                     description='Confirms the user is an adult',
                                     alias='isAdult')
    accept_privacy_and_terms: StrictBoolTrue = Field(...,
                                                     title='Accept privacy and terms',
                                                     description='User accepts Privacy Policy and Terms of Service',
                                                     alias='acceptPrivacyAndTerms')

    @validator('is_adult')
    @classmethod
    def must_be_adult(cls, is_adult):
        '''User must be an adult'''
        if not is_adult:
            raise ValueError('User must be an adult')
        return True

    @validator('accept_privacy_and_terms')
    @classmethod
    def must_accept_priv_and_terms(cls, accepted):
        '''User must accept Privacy policy and Terms and conditions'''
        if not accepted:
            raise ValueError(
                'User must accept Privacy policy and Terms and conditions to use this platform')
        return True


@router.post('/register/', response_model=Message, responses={409: {"model": Message}})
async def register(form: FormRegister,
                   background_tasks: BackgroundTasks,
                   repos: RepoDict = Depends(get_repos)):
    '''Register a new user'''
    uc = uc_user_register.RegisterUseCase(
        repos['user'],
        repos['verif_token'],
        background_tasks
    )

    try:
        req = uc_user_register.RegisterRequest(
            **form.dict()
        )
        await uc.execute(req)
        return {'msg': 'User created successfully'}

    except uc_user_register.UsernameReservedError:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={'msg': 'This is a reserved username'},
        )

    except uc_user_register.UsernameTakenError:
        return JSONResponse(
            status_code=HTTP_409_CONFLICT,
            content={'msg': 'Username already taken'},
        )


class RegisterVerifyBody(BaseModel):
    '''POST model to verify registration'''
    secret: constr(min_length=1)


@router.post('/register/verify/', response_model=Message)
async def verify_registration(token_secret: RegisterVerifyBody,
                              repos: RepoDict = Depends(get_repos)):
    '''User wants to verify his registration'''
    # Setup usecase and usecase request
    uc = uc_user_reg_verify.RegisterVerifyUseCase(
        user_repo=repos['user'],
        vt_repo=repos['verif_token'],
    )
    uc_req = uc_user_reg_verify.RegisterVerifyRequest(
        secret=token_secret.secret
    )

    try:
        # Execute usecase
        uc.execute(uc_req)
        return {'msg': 'Account is verified'}

    except uc_user_reg_verify.InvalidTokenError:
        return JSONResponse(
            status_code=HTTP_409_CONFLICT,
            content={'msg': 'Provided token is not valid'},
        )
