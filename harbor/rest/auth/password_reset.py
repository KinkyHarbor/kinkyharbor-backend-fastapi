'''This module contains all password reset related routes'''

from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from harbor.domain.common import ObjectIdStr, StrongPasswordStr, Message, message_responses
from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.auth import (
    reset_password_exec as uc_user_reset_pw_exec,
    reset_password_req as uc_user_reset_pw_req,
)


router = APIRouter()


class RequestPasswordResetForm(BaseModel):
    '''Form to request a password reset'''
    email: EmailStr


@router.post("/login/request-password-reset/",
             summary='Request mail with password reset link',
             response_model=Message)
async def request_password_reset(form: RequestPasswordResetForm,
                                 background_tasks: BackgroundTasks,
                                 repos: RepoDict = Depends(get_repos)):
    '''User requests a password reset'''
    uc = uc_user_reset_pw_req.RequestPasswordResetUseCase(
        user_repo=repos['user'],
        vt_repo=repos['verif_token'],
        background_tasks=background_tasks,
    )
    uc_req = uc_user_reset_pw_req.RequestPasswordResetRequest(
        email=form.email
    )
    await uc.execute(uc_req)
    return {
        'code': 'reset_sent',
        'msg': 'Verification mail sent, if email is linked to an existing user',
    }


class ExecPasswordResetForm(BaseModel):
    '''Form to execute a password reset'''
    user_id: ObjectIdStr
    token: str
    password: StrongPasswordStr


@router.post("/login/password-reset/",
             summary='Execute password reset',
             response_model=Message,
             responses=message_responses({
                 400: 'Invalid token (Code: invalid_token)',
             }))
async def exec_password_reset(form: ExecPasswordResetForm,
                              repos: RepoDict = Depends(get_repos)):
    '''Verifies password reset token and sets new password'''
    uc = uc_user_reset_pw_exec.ExecResetPasswordUseCase(
        user_repo=repos['user'],
        vt_repo=repos['verif_token'],
    )
    uc_req = uc_user_reset_pw_exec.ExecPasswordResetRequest(**form.dict())

    try:
        result = await uc.execute(uc_req)
        if result == uc_user_reset_pw_exec.ExecResetPasswordResponse.UPDATED:
            return {
                'code': 'password_updated',
                'msg': 'Password is updated',
            }

        if result == uc_user_reset_pw_exec.ExecResetPasswordResponse.UPDATED_AND_VERIFIED:
            return {
                'code': 'updated_and_verified',
                'msg': 'Password is updated and account is verified',
            }

    except uc_user_reset_pw_exec.InvalidTokenError:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={
                'code': 'invalid_token',
                'msg': 'Invalid token',
            }
        )
