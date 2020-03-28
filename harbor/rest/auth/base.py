'''This module contains all authentication related routes'''

from fastapi import APIRouter

from harbor.rest.auth import (
    login as router_login,
    password_reset as router_pw_reset,
    refresh as router_refresh,
    register as router_register,
)

# Combine all auth routers
router = APIRouter()
router.include_router(router_login.router)
router.include_router(router_pw_reset.router)
router.include_router(router_refresh.router)
router.include_router(router_register.router)
