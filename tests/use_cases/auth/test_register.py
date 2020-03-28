'''Unit tests for Register User usecase'''
# pylint: disable=unused-argument

import pytest

from harbor.use_cases.auth import register as uc_user_reg


@pytest.fixture(name='uc_req')
def fixture_uc_req():
    '''Returns a register request'''
    # with pytest.raises(ValueError):
    uc_user_reg.RegisterRequest(
        display_name='TestUser',
        email='user@kh.test',
        password='VeryStrongTestPassword',
        is_adult=True,
        accept_privacy_and_terms=True,
    )


def test_success(uc_req):
    '''Should register a user'''
