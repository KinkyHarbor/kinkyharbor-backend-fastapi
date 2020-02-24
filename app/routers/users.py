from fastapi import APIRouter, Depends

from models.user import User
from core.auth import get_current_active_user

router = APIRouter()


@router.get('/me')
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
