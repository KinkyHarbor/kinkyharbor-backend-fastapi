'''This module handles all routes for notifications operations'''

from datetime import datetime
from enum import Enum, unique
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST

from harbor.domain.common import ObjectIdStr, message_responses
from harbor.domain.notification import Notification
from harbor.domain.token import AccessTokenData
from harbor.rest.auth.base import validate_access_token
from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.notifications import (
    get_recent as uc_recent,
    get_historic as uc_historic,
    mark_as_read as uc_mark_read,
)

router = APIRouter()


@router.get('/',
            summary='Get recent notifications',
            response_model=List[Notification],
            response_model_by_alias=False)
async def get_recent(token_data: AccessTokenData = Depends(validate_access_token),
                     repos: RepoDict = Depends(get_repos)):
    '''A recent notification is either not read yet or is maximum one week old'''
    uc = uc_recent.GetRecentUsecase(notif_repo=repos['notification'])
    uc_req = uc_recent.GetRecentRequest(
        user_id=token_data.user_id,
    )
    return await uc.execute(uc_req)


class GetHistoricNotificationsForm(BaseModel):
    '''Form to request historic notifications'''
    from_: datetime = Field(..., alias="from")
    to: datetime


@router.post('/get-historic/',
             summary='Get historic notifications',
             response_model=List[Notification],
             response_model_by_alias=False,
             responses=message_responses({
                 400: 'Maximum time range of 90 days exceeded',
             }))
async def get_historic(form: GetHistoricNotificationsForm,
                       token_data: AccessTokenData = Depends(
                           validate_access_token),
                       repos: RepoDict = Depends(get_repos)):
    '''Returns all notifications between 2 timestamps.
    Maximum allowed time range is 90 days.
    Timestamps are in UTC.
    '''
    uc = uc_historic.GetHistoricUsecase(notif_repo=repos['notification'])
    uc_req = uc_historic.GetHistoricRequest(
        user_id=token_data.user_id,
        from_=form.from_,
        to=form.to,
    )

    try:
        return await uc.execute(uc_req)

    except uc_historic.MaxTimeRangeExceeded:
        return JSONResponse(
            status_code=HTTP_400_BAD_REQUEST,
            content={
                'code': 'max_time_range_exceeded',
                'msg': 'Maximum time range of 90 days exceeded',
            },
        )


@unique
class MarkAs(str, Enum):
    '''Mark notification as read or unread'''
    READ = 'READ'
    UNREAD = 'UNREAD'


class MarkNotificationAsForm(BaseModel):
    '''Form to mark notifications as read or unread'''
    notification_ids: List[ObjectIdStr]
    mark_as: MarkAs


class MarkNotificationAsResponse(BaseModel):
    '''Response to mark notifications as read or unread'''
    count_updated: int


@router.post('/mark-as-read/',
             summary="Mark multiple notifications as read or unread",
             response_model=MarkNotificationAsResponse)
async def mark_as(form: MarkNotificationAsForm,
                  token_data: AccessTokenData = Depends(validate_access_token),
                  repos: RepoDict = Depends(get_repos)):
    '''Mark multiple notifications as read or unread'''
    # Prepare use case and request
    uc = uc_mark_read.MarkAsReadUsecase(notif_repo=repos['notification'])
    uc_req = uc_mark_read.MarkAsReadRequest(
        user_id=token_data.user_id,
        notifications=form.notification_ids,
        is_read=(form.mark_as == MarkAs.READ)
    )

    # Call use case and return results
    result = await uc.execute(uc_req)
    return MarkNotificationAsResponse(count_updated=result.count_updated)
