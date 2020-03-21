from pydantic import BaseModel

from harbor.repository.base import UserRepo
from harbor.response_objects import common as res


class LoginRequest(BaseModel):
    login: str
    password: str


class LoginUseCase:

    def __init__(self, repo: UserRepo):
        self.repo = repo

    def execute(self, req: LoginRequest):
        try:
            user = self.repo.get_by_login(req.login)
            return res.ResponseSuccess(user)
        except Exception as exc:
            return res.ResponseFailure.build_system_error(
                "{}: {}".format(exc.__class__.__name__, "{}".format(exc)))
