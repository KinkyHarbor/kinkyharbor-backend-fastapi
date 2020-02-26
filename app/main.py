'''Main entry point for Kinky Harbor'''

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from routers import auth, users


app = FastAPI()
app.include_router(
    auth.router,
    tags=['auth'])
app.include_router(
    users.router,
    prefix='/users',
    tags=['users']
)


@app.get('/', include_in_schema=False)
async def redirect_to_docs():
    '''Redirect root page to docs.'''
    return RedirectResponse(url='/docs')


# Allows debugging of the application
# https://fastapi.tiangolo.com/tutorial/debugging/
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
