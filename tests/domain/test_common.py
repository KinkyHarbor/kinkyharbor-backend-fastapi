'''Unit tests for common domain'''

import pytest
from pydantic import BaseModel, ValidationError

from harbor.domain import common


class StrictBoolTrueModel(BaseModel):
    '''Model to test StrictBool'''
    value: common.StrictBoolTrue


def test_success_strictbooltrue_value_true():
    '''Should return no error is value is True'''
    StrictBoolTrueModel(value=True)


def test_fail_strictbooltrue_value_false():
    '''Should throw error if value is not True'''
    with pytest.raises(ValidationError) as info:
        StrictBoolTrueModel(value=False)
    assert info.value.errors()[0]['type'] == "value_error"


@pytest.mark.parametrize("value", [0, 1, "True"])
def test_fail_strictbooltrue_type_incorrect(value):
    '''Should throw error if type of value is not a bool'''
    with pytest.raises(ValidationError) as info:
        StrictBoolTrueModel(value=value)
    assert info.value.errors()[0]['type'] == "type_error"
