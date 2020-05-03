'''This module handles all routes for notifications operations'''

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from harbor.domain.notification import Notification
from harbor.domain.token import AccessTokenData
from harbor.repository.base import RepoDict, get_repos
from harbor.rest.auth.base import validate_access_token

router = APIRouter()


def random_uuid(length=10):
    '''Returns a part of a UUIDv4'''
    uuid_str = str(uuid.uuid4()).replace('-', '')
    if 0 < length <= len(uuid_str):
        return uuid_str[:length]
    return uuid_str


class CreateNotificationForm(BaseModel):
    '''Form to create a notification'''
    is_read: bool
    created_on: datetime = None


@router.post('/create-notification/',
             summary='Create notification',
             response_model=Notification,
             response_model_by_alias=False)
async def create_notification(form: CreateNotificationForm,
                              token_data: AccessTokenData = Depends(
                                  validate_access_token),
                              repos: RepoDict = Depends(get_repos)):
    '''Create a single debug notification'''
    appendix = random_uuid()
    notif = Notification(
        user_id=token_data.user_id,
        title=f"Debug title {appendix}",
        description=f"A quite long debug descripion to test {appendix}",
        icon="https://kinkyharbor.com/favicon.ico",
        link="/profile/me",
        **form.dict(exclude_none=True),
    )
    notif.id = await repos['notification'].add(notif)
    return notif
