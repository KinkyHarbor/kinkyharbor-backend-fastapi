'''User logs in to API'''

from pydantic import BaseModel, constr

from harbor.core import auth
from harbor.repository.base import UserRepo, RefreshTokenRepo


class LoginRequest(BaseModel):
    '''Request for login usecase'''
    login: constr(min_length=1)
    password: constr(min_length=1)


class LoginResponse(BaseModel):
    '''Response of login usecase'''
    access_token: str
    refresh_token: str


class InvalidCredsError(Exception):
    '''Provided credentials are invalid'''


class UserLockedError(Exception):
    '''User is locked'''


class LoginUseCase:
    '''User logs in to API'''

    def __init__(self, user_repo: UserRepo, rt_repo: RefreshTokenRepo):
        self.user_repo = user_repo
        self.rt_repo = rt_repo

    async def execute(self, req: LoginRequest) -> LoginResponse:
        '''Exchanges credentials for access and refresh token

        Raises:
            InvalidCredsError: Provided credentials are invalid
            UserLockedError: User is locked
        '''
        login = req.login.lower()
        user = await self.user_repo.get_by_login(login)

        # Check if matching user was found
        if not user:
            # Prevent timing attack
            auth.get_password_hash(req.password)
            raise InvalidCredsError()

        # Check if password is correct
        if not auth.verify_password(req.password, user.password_hash):
            raise InvalidCredsError()

        # Check if user is not locked
        if user.is_locked:
            raise UserLockedError()

        # Authentication successful
        await self.user_repo.update_last_login(user.id)

        # Generate tokens
        access_token = await auth.create_access_token(data={"sub": f'user:{user.id}'})
        refresh_token = await self.rt_repo.create_token(user.id)

        # Return results
        return LoginResponse(
            access_token=access_token,
            refresh_token=f'{user.id}:{refresh_token.secret}',
        )
