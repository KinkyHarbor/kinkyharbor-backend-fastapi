from fastapi import Depends, FastAPI

from core.auth import get_current_user
from routers import auth, users


app = FastAPI()
app.include_router(auth.router)
app.include_router(
    users.router,
    prefix='/users',
    tags=['users']
)


@app.get('/items/')
async def read_items(token: str = Depends(get_current_user)):
    return {'token': token}
