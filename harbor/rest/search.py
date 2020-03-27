'''This module handles all routes for search operations'''

from fastapi import APIRouter, Depends

from harbor.core.auth import validate_access_token
from harbor.domain.token import AccessTokenData
from harbor.repository.base import RepoDict, get_repos
from harbor.use_cases.search import (
    generic as uc_gen_search,
)

router = APIRouter()


@router.get('/',
            summary='Search for people, pages, groups and events',
            response_model=uc_gen_search.GenericSearchResponse)
async def search(q: str,
                 token_data: AccessTokenData = Depends(validate_access_token),
                 repos: RepoDict = Depends(get_repos)):
    '''Search for people, pages, groups and events'''
    uc = uc_gen_search.GenericSearchUseCase(user_repo=repos['user'])
    uc_req = uc_gen_search.GenericSearchRequest(
        query=q,
        user_id=token_data.user_id,
    )
    return await uc.execute(uc_req)
