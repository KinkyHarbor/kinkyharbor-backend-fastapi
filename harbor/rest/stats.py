'''This module handles all routes for stats operations'''

from datetime import date
from typing import Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.stats import get_active_user_count as uc_count

router = APIRouter()


class ActiveUserCountResponse(BaseModel):
    '''Response for active user count'''
    now: int
    history: Dict[date, int]


@router.get('/active-users',
            summary='Get active user count',
            response_model=ActiveUserCountResponse,
            response_model_by_alias=False)
async def active_users(repos: RepoDict = Depends(get_repos)):
    '''Returns current and historic active user count.
    We consider users as active, if their last login is less than one month ago.
    Historic counts are the averages per month for the past year.
    '''
    uc = uc_count.GetActiveUserCountUsecase(stats_repo=repos['stats'])
    res = await uc.execute()
    return ActiveUserCountResponse(
        now=res.now,
        history=res.history.values,
    )
