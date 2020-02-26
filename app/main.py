'''Main entry point for Kinky Harbor'''

import uvicorn
from fastapi import FastAPI

from routers import auth, users


app = FastAPI()
app.include_router(auth.router)
app.include_router(
    users.router,
    prefix='/users',
    tags=['users']
)

# Allows debugging of the application
# https://fastapi.tiangolo.com/tutorial/debugging/
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
