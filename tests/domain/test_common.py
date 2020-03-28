'''Unit tests for common domain'''

import pytest
from pydantic import BaseModel, ValidationError

from harbor.domain import common

# ================================
# =        StrictBoolTrue        =
# ================================


class StrictBoolTrueModel(BaseModel):
    '''Model to test StrictBool'''
    value: common.StrictBoolTrue


def test_success_strictbooltrue_value_true():
    '''Should return no error if value is True'''
    StrictBoolTrueModel(value=True)


def test_fail_strictbooltrue_value_false():
    '''Should throw error if value is not True'''
    with pytest.raises(ValidationError) as info:
        StrictBoolTrueModel(value=False)
    err = info.value.errors()[0]
    assert err['type'] == "value_error"
    assert "True" in err['msg']


@pytest.mark.parametrize("value", [0, 1, "True"])
def test_fail_strictbooltrue_type_incorrect(value):
    '''Should throw error if type of value is not a bool'''
    with pytest.raises(ValidationError) as info:
        StrictBoolTrueModel(value=value)
    err = info.value.errors()[0]
    assert err['type'] == "type_error"
    assert "bool" in err['msg'].lower()


# ================================
# =        DisplayNameStr        =
# ================================

class DisplayNameStrModel(BaseModel):
    '''Model to test DisplayNameStr'''
    name: common.DisplayNameStr


@pytest.mark.parametrize("name", ["TestA", "123", "1_2", "-"])
def test_success_displaynamestr_valid_names(name):
    '''Should return no error'''
    DisplayNameStrModel(name=name)


def test_fail_displaynamestr_is_empty():
    '''Should return ValueError as empty string is not allowed'''
    with pytest.raises(ValidationError) as info:
        DisplayNameStrModel(name="")
    err = info.value.errors()[0]
    assert err['type'] == 'value_error'
    assert "empty" in err['msg'].lower()


@pytest.mark.parametrize("name_len", [41, 100, 10000])
def test_fail_displaynamestr_too_long(name_len):
    '''Should return ValueError as max lenght is 40 chars'''
    with pytest.raises(ValidationError) as info:
        DisplayNameStrModel(name="T"*name_len)
    err = info.value.errors()[0]
    assert err['type'] == 'value_error'
    assert "too long" in err['msg'].lower()


@pytest.mark.parametrize("name", ["Test?", "/", "Test.A", "<test>"])
def test_fail_displaynamestr_invalid_chars(name):
    '''Should return ValueError as characters are invalid'''
    with pytest.raises(ValidationError) as info:
        DisplayNameStrModel(name=name)
    err = info.value.errors()[0]
    assert err['type'] == 'value_error'
    assert "invalid" in err['msg'].lower()
