'''This module contains reusable fields and mixins'''

import re
from typing import Optional, Union, Dict, Any
from bson.objectid import ObjectId

from pydantic import BaseModel, Field


class StrictBoolTrue(int):
    '''Bool which must be True'''
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None:
        field_schema.update(type='boolean')

    @classmethod
    def validate(cls, value):
        '''Check if True'''
        if not isinstance(value, bool):
            raise TypeError('Value must be a bool')
        if not bool(value):
            raise ValueError('Value must be True')
        return True


class DisplayNameStr(str):
    '''Display name of a user'''
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, name):
        '''Check if display name matches criteria'''
        if len(name) > 40:
            raise ValueError("Name is too long. Max 40 characters allowed.")

        match = re.search(r'[^a-zA-Z0-9_\-]', name)
        if match:
            raise ValueError(
                "Name should only contain alphanumerical "
                "characters, '-' or '_'. Invalid character: " +
                match.group())
        return name


class StrongPasswordStr(str):
    '''Only allow strong passwords'''
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, password):
        '''Check if  password is strong enough

        Password should either be 16 characters or longer (passphrase).
        Or should be minimum 8 long and have lower case, upper case and a digit.
        '''
        if len(password) >= 16:
            # Password is passphrase
            return password

        if len(password) < 8:
            raise ValueError('Password is too short. Minimum length is 8.')

        if re.search('[a-z]', password) is None:
            raise ValueError(
                'Password should contain at least one lower case character.')

        if re.search('[A-Z]', password) is None:
            raise ValueError(
                'Password should contain at least one upper case character.')

        if re.search('[0-9]', password) is None:
            raise ValueError(
                'Password should contain at least one digit.')

        # Password is strong enough
        return password


class ObjectIdStr(str):
    '''String containing a MongoDB ObjectID'''
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, object_id: Union[str, ObjectId]):
        '''Check if string is a valid ObjectID'''
        if not ObjectId.is_valid(str(object_id)):
            return ValueError(f"Not a valid ObjectId: {object_id}")
        return str(object_id)


class DBModelMixin(BaseModel):
    '''Mixin to add an ID to a Pydantic model'''
    id: Optional[ObjectIdStr] = Field(None, alias="_id")

    class Config:
        '''Configuration of DBModelMixin'''
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class Message(BaseModel):
    '''Basic response with message'''
    msg: str
