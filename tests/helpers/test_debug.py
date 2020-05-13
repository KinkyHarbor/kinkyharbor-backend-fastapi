'''Unit tests for Debug helpers'''

import pytest

from harbor.helpers.debug import is_harbor_file


@pytest.mark.parametrize('filename,expected', [
    ('harbor', True),
    ('python', False),
    ('importlib', False),
    ('test', False),
    ('harbor/python', False),
    ('harbor/importlib', False),
])
def test_is_harbor_file(filename, expected):
    '''Should check if file is a Harbor file'''
    abs_name = f'/{filename}/test.py'
    assert is_harbor_file(abs_name) == expected
