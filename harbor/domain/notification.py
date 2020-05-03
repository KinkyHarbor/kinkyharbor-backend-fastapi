'''This module contains all notification related models'''

from pydantic import HttpUrl

from harbor.domain.common import CreatedOnMixin, DBModelMixin, ObjectIdStr


class Notification(DBModelMixin, CreatedOnMixin):
    '''Notification'''
    user_id: ObjectIdStr
    title: str
    description: str = None
    is_read: bool = False
    icon: HttpUrl
    link: str
