'''Main entry point for Kinky Harbor'''

import logging

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware

from harbor.helpers.settings import get_settings
from harbor.repository.mongo import (
    notifications as mongo_notif,
    refresh_tokens as mongo_rt,
    stats as mongo_stats,
    users as mongo_user,
    verif_tokens as mongo_vt,
)
from harbor.rest.auth import base as router_auth
from harbor.rest import (
    notifications as router_notif,
    search as router_search,
    stats as router_stats,
    users as router_users,
)


# Start app
app = FastAPI(
    title='Kinky Harbor',
    description='Welcome to Kinky Harbor! Your safe harbor.',
    version='alpha',
)

# Add routers
# Auth
app.include_router(
    router_auth.router,
    prefix='/auth',
    tags=['Auth']
)
# Notifications
app.include_router(
    router_notif.router,
    prefix='/notifications',
    tags=['Notifications'],
)
# Search
app.include_router(
    router_search.router,
    prefix='/search',
    tags=['Search'],
)
# Stats
app.include_router(
    router_stats.router,
    prefix='/stats',
    tags=['Stats'],
)
# Users
app.include_router(
    router_users.router,
    prefix='/users',
    tags=['Users'],
)

# Connect to database
@app.on_event('startup')
async def create_repos():
    '''Creates repositories on application start'''
    logging.info("Database repositories: Creating ...")
    app.state.repos = {
        'notification': await mongo_notif.create_repo(),
        'refresh_token': await mongo_rt.create_repo(),
        'stats': await mongo_stats.create_repo(),
        'user': await mongo_user.create_repo(),
        'verif_token': await mongo_vt.create_repo()
    }
    logging.info("Database repositories: Created")

# Close database connections
@app.on_event("shutdown")
async def close_repos():
    '''Close DB client of repositories on application shutdown'''
    logging.info("Database repositories: Closing ...")
    await app.state.repos['notification'].close()
    await app.state.repos['refresh_token'].close()
    await app.state.repos['stats'].close()
    await app.state.repos['user'].close()
    await app.state.repos['verif_token'].close()
    logging.info("Database repositories: Closed")


# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().CORS,
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
