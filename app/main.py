'''Main entry point for Kinky Harbor'''

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from routers import auth
from routers import users as router_users
from core.db import create_db_client
from crud import users, verif_tokens


def add_database_events(server: FastAPI) -> None:
    '''Creates a database client on application start'''
    @server.on_event('startup')
    async def connect_to_database() -> None:
        db = create_db_client()
        server.state.db = db

        # Ensure indexes
        await users.ensure_indexes(db)
        await verif_tokens.ensure_indexes(db)


# Start app
app = FastAPI()
app.include_router(
    auth.router,
    prefix='/auth',
    tags=['auth'])
app.include_router(
    router_users.router,
    prefix='/users',
    tags=['users']
)
add_database_events(app)

# CORS
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', include_in_schema=False)
async def redirect_to_docs():
    '''Redirect root page to docs.'''
    return RedirectResponse(url='/docs')


# Allows debugging of the application
# https://fastapi.tiangolo.com/tutorial/debugging/
if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
