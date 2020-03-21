from pydantic import BaseModel, EmailStr, validator, Field

from harbor.domain.common import DisplayNameStr, StrongPasswordStr


class RegisterUser(BaseModel):
    '''Required form data for registering a user'''
    username: DisplayNameStr
    email: EmailStr
    password: StrongPasswordStr = Field(...,
                                        description='Password should either be 16 characters or '
                                        'longer (passphrase). Or should be minimum 8 long and '
                                        'have lower case, upper case and a digit.')
    isAdult: bool = Field(...,
                          title='Is adult',
                          description='Confirms the user is an adult')
    acceptPrivacyAndTerms: bool

    @validator('isAdult')
    @classmethod
    def must_be_adult(cls, is_adult):
        '''User must be an adult'''
        if not is_adult:
            raise ValueError('User must be an adult')
        return True

    @validator('acceptPrivacyAndTerms')
    @classmethod
    def must_accept_priv_and_terms(cls, accepted):
        '''User must accept Privacy policy and Terms and conditions'''
        if not accepted:
            raise ValueError(
                'User must accept Privacy policy and Terms and conditions to use this platform')
        return True
