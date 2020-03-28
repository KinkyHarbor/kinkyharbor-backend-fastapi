'''Main entry point for Kinky Harbor'''

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from harbor.core import settings
from harbor.repository.mongo import (
    refresh_tokens as mongo_rt,
    users as mongo_user,
    verif_tokens as mongo_vt,
)
from harbor.rest.auth import base as router_auth
from harbor.rest import (
    search as router_search,
    users as router_users,
)


# Start app
app = FastAPI()

# Add routers
# Auth
app.include_router(
    router_auth.router,
    prefix='/auth',
    tags=['auth']
)
# Search
app.include_router(
    router_search.router,
    prefix='/search',
    tags=['search'],
)
# Users
app.include_router(
    router_users.router,
    prefix='/users',
    tags=['users'],
)

# Connect to database
@app.on_event('startup')
async def create_repos() -> None:
    '''Creates repositories on application start'''
    app.state.repos = {
        'refresh_token': await mongo_rt.create_repo(),
        'user': await mongo_user.create_repo(),
        'verif_token': await mongo_vt.create_repo()
    }

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS,
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
