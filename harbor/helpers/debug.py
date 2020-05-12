'''Helpers module for debug related functions'''

import logging


def log_call(module_name, function_name, args):
    '''Log a function call'''
    message = '%s: "%s" called with args: %r'
    logging.debug(message, module_name, function_name, args)
