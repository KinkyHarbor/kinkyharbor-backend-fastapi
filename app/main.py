import uvicorn
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
