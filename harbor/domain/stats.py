'''This module contains all statistics related models'''

from datetime import datetime, date
from enum import Enum, unique
from typing import Dict

from pydantic import BaseModel


@unique
class ReadingSubject(str, Enum):
    '''Supported reading subjects'''
    ACTIVE_USERS = 'active_users'


class Reading(BaseModel):
    '''Statistics reading'''
    datetime: datetime
    subject: ReadingSubject
    value: int
    unit: str


class ReadingAggregationTimespan(int, Enum):
    '''Timespan of aggregated reading in days'''
    WEEK = 7
    MONTH = 30
    YEAR = 365


class ReadingAggregationOperation(str, Enum):
    '''Operation of aggregated reading'''
    AVERAGE = 'avg'


class ReadingAggregation(BaseModel):
    '''Aggregation of readings'''
    subject: ReadingSubject
    timespan: ReadingAggregationTimespan
    operation: ReadingAggregationOperation
    values: Dict[date, int]
