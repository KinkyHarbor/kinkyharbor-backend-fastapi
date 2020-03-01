'''This module contains all email related models'''

from email.headerregistry import Address

from pydantic import BaseModel


class EmailMsg(BaseModel):
    recipient: Address
    subject: str
    text: str
    html: str

    class Config:
        '''Pydantic config'''
        arbitrary_types_allowed = True