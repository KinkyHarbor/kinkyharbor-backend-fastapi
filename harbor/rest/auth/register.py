'''This module contains all registration related routes'''

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, constr, EmailStr, Field
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_409_CONFLICT

from harbor.domain.common import (StrictBoolTrue, DisplayNameStr,
                                  StrongPasswordStr, Message, message_responses)
from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.auth import (
    register as uc_user_register,
    register_verify as uc_user_reg_verify,
)


router = APIRouter()


class RegisterForm(BaseModel):
    '''Required form data for registering a user'''
    display_name: DisplayNameStr = Field(..., alias='username')
    email: EmailStr
    password: StrongPasswordStr = Field(
        ...,
        description='Password should either be 16 characters or '
        'longer (passphrase). Or should be minimum 8 long and '
        'have lower case, upper case and a digit.'
    )
    is_adult: StrictBoolTrue = Field(
        ...,
        title='Is adult',
        description='Confirms the user is an adult',
        alias='isAdult'
    )
    accept_privacy_and_terms: StrictBoolTrue = Field(
        ...,
        title='Accept privacy and terms',
        description='User accepts Privacy Policy and Terms of Service',
        alias='acceptPrivacyAndTerms'
    )


@router.post('/register/',
             summary='Register and mail verification link',
             response_model=Message,
             responses=message_responses({
                 403: 'Username is reserved (Code: reserved_username)',
                 409: 'Username already taken (Code: username_taken)',
             }))
async def register(form: RegisterForm,
                   background_tasks: BackgroundTasks,
                   repos: RepoDict = Depends(get_repos)):
    '''Register a new user and send verification link'''
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
        return {
            'code': 'account_created',
            'msg': 'Account created',
        }

    except uc_user_register.UsernameReservedError:
        return JSONResponse(
            status_code=HTTP_403_FORBIDDEN,
            content={
                'code': 'reserved_username',
                'msg': 'Username is reserved',
            },
        )

    except uc_user_register.UsernameTakenError:
        return JSONResponse(
            status_code=HTTP_409_CONFLICT,
            content={
                'code': 'username_taken',
                'msg': 'Username already taken',
            },
        )


class VerifyRegistrationForm(BaseModel):
    '''POST model to verify registration'''
    token: constr(min_length=1)


@router.post('/register/verify/',
             summary='Execute registration verification',
             response_model=Message,
             responses=message_responses({
                 400: 'Invalid token (Code: invalid_token)',
             }))
async def verify_registration(form: VerifyRegistrationForm,
                              repos: RepoDict = Depends(get_repos)):
    '''User wants to verify his registration'''
    # Setup usecase and usecase request
    uc = uc_user_reg_verify.RegisterVerifyUseCase(
        user_repo=repos['user'],
        vt_repo=repos['verif_token'],
    )
    uc_req = uc_user_reg_verify.RegisterVerifyRequest(
        secret=form.token
    )

    try:
        # Execute usecase
        await uc.execute(uc_req)
        return {
            'code': 'account_verified',
            'msg': 'Account verified',
        }

    except uc_user_reg_verify.InvalidTokenError:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={
                'code': 'invalid_token',
                'msg': 'Invalid token',
            },
        )
