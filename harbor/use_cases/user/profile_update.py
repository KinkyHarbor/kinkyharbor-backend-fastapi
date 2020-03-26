from pydantic import BaseModel


class UpdateUser(BaseModel):
    '''Info which allows direct update'''
    bio: str = None
    gender: str = None
