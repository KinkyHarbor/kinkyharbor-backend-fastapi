'''Base classes for repositories'''

from abc import ABC, abstractmethod
from typing import List, Dict

from starlette.requests import Request

from harbor.domain.common import ObjectIdStr
from harbor.domain.token import RefreshToken, VerificationToken
from harbor.domain.token import VerificationTokenRequest as VerifTokenReq
from harbor.domain.token import VerificationPurposeEnum as VerifPur
from harbor.domain.user import BaseUser, User, UserWithPassword, UserFlags


class Repo(ABC):
    '''Base class for repositories to support typing'''


RepoDict = Dict[str, Repo]


def get_repos(request: Request) -> RepoDict:
    '''Returns instance of all repositories from request'''
    return request.app.state.repos


class RefreshTokenRepo(Repo):
    '''Repository for refresh tokens'''
    @abstractmethod
    async def create_token(self, user_id: ObjectIdStr) -> RefreshToken:
        '''Creates and returns a verification token'''

    @abstractmethod
    async def replace_token(self, token: RefreshToken) -> RefreshToken:
        '''Replaces a refresh token

        Returns
            RefreshToken: Token is valid, new token is returned
            None: Token is invalid
        '''

class UsernameTakenError(Exception):
    '''Username is already taken'''

class UserRepo(Repo):
    '''Repository for users'''
    @abstractmethod
    async def get(self, user_id: str) -> User:
        '''Return single user by ID'''

    @abstractmethod
    async def get_by_login(self, login: str) -> UserWithPassword:
        '''Get single user by username or email'''

    @abstractmethod
    async def get_by_username(self, username: str) -> User:
        '''Get single user by username'''

    @abstractmethod
    async def get_search(self, user_id: str,
                         search_string: str,
                         limit: int = 10) -> List[BaseUser]:
        '''Search users based on username'''

    @abstractmethod
    async def add(self,
                  display_name: str,
                  email: str,
                  password_hash: str) -> User:
        '''Add a new user

        Raises:
            UsernameTakenError: Username is already in use
        '''

    @abstractmethod
    async def set_password(self, user_id: str, password_hash: str) -> User:
        '''Sets a new password for the user'''

    @abstractmethod
    async def set_flag(self, user_id: str, flag: UserFlags, value: bool) -> User:
        '''Sets a flag on the user to True or False

        Returns
            User: Updated user
        '''

    @abstractmethod
    async def set_info(self, user_id: str, user_info: Dict) -> User:
        '''Sets info which allows direct update

        Returns
            User: Updated user
        '''

    @abstractmethod
    async def update_last_login(self, user_id: str):
        '''Updates last login timestamp for user'''


class VerifTokenRepo(Repo):
    '''Repository for verification tokens'''
    @abstractmethod
    async def create_verif_token(self, user_id: str, purpose: VerifPur) -> VerificationToken:
        '''Creates and returns a verification token'''

    @abstractmethod
    async def verify_verif_token(self, token: VerifTokenReq) -> VerificationToken:
        '''Verifies a verification token

        Returns
            VerificationToken: Token is valid
            None: Token is invalid
        '''
