'''Helpers module for debug related functions'''

import logging


def log_call(module_name, function_name, args):
    '''Log a function call'''
    message = '%s: "%s" called with args: %r'
    logging.debug(message, module_name, function_name, args)


def trace_calls(frame, event, arg):
    '''Trace function to print calls

    See https://pymotw.com/2/sys/tracing.html for more info
    '''
    # Only trace function calls
    if event != 'call':
        return

    # Extract information
    caller = frame.f_back
    caller_line_no = caller.f_lineno
    caller_filename = caller.f_code.co_filename
    target = frame.f_code
    func_name = target.co_name
    func_line_no = frame.f_lineno
    func_filename = target.co_filename

    # Only trace Harbor files
    if 'python' in caller_filename or 'python' in func_filename:
        return

    # Log trace
    message = '%s:%s called "%s" (%s:%s)'
    logging.debug(message,
                  func_filename,
                  func_line_no,
                  func_name,
                  caller_line_no,
                  caller_filename)
