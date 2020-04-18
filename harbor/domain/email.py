'''This module contains all email related models'''

from enum import Enum, unique

from pydantic import BaseModel, EmailStr


class EmailMsg(BaseModel):
    '''Email message'''
    to_name: str
    to_email: EmailStr
    subject: str
    text: str
    html: str


@unique
class EmailSecurity(str, Enum):
    '''Security options for SMTP'''
    TLS_SSL = 'tls_ssl'
    STARTTLS = 'starttls'
    UNSECURE = 'unsecure'
