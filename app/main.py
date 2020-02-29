'''Main entry point for Kinky Harbor'''

import logging

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from routers import auth, users
from db import mongo


def add_database_events(server: FastAPI) -> None:
    @server.on_event("startup")
    async def connect_to_database() -> None:
        db = mongo.create_db_client()
        server.state.db = db

        # Ensure indexes
        await db.users.create_index("username", unique=True)
        await db.users.create_index("email", unique=True)


app = FastAPI()
app.include_router(
    auth.router,
    tags=['auth'])
app.include_router(
    users.router,
    prefix='/users',
    tags=['users']
)
add_database_events(app)


@app.get('/', include_in_schema=False)
async def redirect_to_docs():
    '''Redirect root page to docs.'''
    return RedirectResponse(url='/docs')


# Allows debugging of the application
# https://fastapi.tiangolo.com/tutorial/debugging/
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
