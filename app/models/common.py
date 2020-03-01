'''This module contains reusable fields and mixins'''

import re
from typing import Optional, Union
from bson.objectid import ObjectId

from pydantic import BaseModel, Field


class DisplayNameStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, name):
        if len(name) > 40:
            raise ValueError("Name is too long. Max 40 characters allowed.")

        match = re.search(r'[^a-zA-Z0-9_\-]', name)
        if match:
            raise ValueError(
                "Name should only contain alphanumerical "
                "characters, '-' or '_'. Invalid character: " +
                match.group())
        return name


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, object_id: Union[str, ObjectId]):
        if not ObjectId.is_valid(str(object_id)):
            return ValueError(f"Not a valid ObjectId: {object_id}")
        return str(object_id)


class DBModelMixin(BaseModel):
    id: Optional[ObjectIdStr] = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
