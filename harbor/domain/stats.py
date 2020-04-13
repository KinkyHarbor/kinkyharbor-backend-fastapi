'''This module contains all statistics related models'''

from datetime import datetime

from pydantic import BaseModel


class Reading(BaseModel):
    '''Statistics reading'''
    datetime: datetime
    subject: str
    value: int
    unit: str
