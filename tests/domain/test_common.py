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


# ================================
# =       StrongPasswordStr      =
# ================================

class StrongPasswordStrModel(BaseModel):
    '''Model to test StrongPasswordStr'''
    passwd: common.StrongPasswordStr


@pytest.mark.parametrize("name_len", [16, 100, 10000])
def test_success_strongpwstr_valid_passphrase(name_len):
    '''Should accept any passphrase (min 16 chars)'''
    StrongPasswordStrModel(passwd="T"*name_len)


@pytest.mark.parametrize("name", ["TestPass1", "Secure12", "123HaRbOr"])
def test_success_strongpwstr_valid_password(name):
    '''Should accept valid passwords'''
    StrongPasswordStrModel(passwd=name)


@pytest.mark.parametrize("pass_len", [1, 7])
def test_fail_strongpwstr_too_short(pass_len):
    '''Should return ValueError as password requires at least 8 chars'''
    with pytest.raises(ValidationError) as info:
        StrongPasswordStrModel(passwd="T"*pass_len)
    err = info.value.errors()[0]
    assert err['type'] == 'value_error'
    assert "too short" in err['msg'].lower()


def test_fail_strongpwstr_no_uppercase():
    '''Should return ValueError as password requires at least 1 upper case char'''
    with pytest.raises(ValidationError) as info:
        StrongPasswordStrModel(passwd="insecure123")
    err = info.value.errors()[0]
    assert err['type'] == 'value_error'
    assert "upper case" in err['msg'].lower()


def test_fail_strongpwstr_no_lowercase():
    '''Should return ValueError as password requires at least 1 lower case char'''
    with pytest.raises(ValidationError) as info:
        StrongPasswordStrModel(passwd="INSECURE123")
    err = info.value.errors()[0]
    assert err['type'] == 'value_error'
    assert "lower case" in err['msg'].lower()


def test_fail_strongpwstr_no_digit():
    '''Should return ValueError as password requires at least 1 digit'''
    with pytest.raises(ValidationError) as info:
        StrongPasswordStrModel(passwd="Insecure")
    err = info.value.errors()[0]
    assert err['type'] == 'value_error'
    assert "digit" in err['msg'].lower()

# ================================
# =          ObjectIdStr         =
# ================================


class ObjectIdStrModel(BaseModel):
    '''Model to test ObjectIdStr'''
    obj_id: common.ObjectIdStr


@pytest.mark.parametrize("obj_id", ['5e7f656765f1b64f3f7f69f2', '507f191e810c19729de860ea'])
def test_success_objectidstr_valid_id(obj_id):
    '''Should return no error'''
    ObjectIdStrModel(obj_id=obj_id)


@pytest.mark.parametrize("obj_id", ['5e7f656765f1b64f3f7f69f', '507f191e810c19729de860ez'])
def test_fail_objectidstr_invalid_id(obj_id):
    '''Should return ValueError (too short and not hex)'''
    with pytest.raises(ValidationError) as info:
        ObjectIdStrModel(obj_id=obj_id)
    err = info.value.errors()[0]
    assert err['type'] == 'value_error'
    assert "invalid" in err['msg'].lower()
