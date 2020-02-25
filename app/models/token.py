from pydantic import BaseModel
from db.models import DBModelMixin


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(DBModelMixin):
    pass
