"""Exception handling functions"""
import sys
import logging
import linecache

def print_exception():
    """ Prints stack along with message : Use when swallowing an exception"""
    # DEPRECATED: Use logger.log_update_exception() instead
    _, exc_obj, _tb = sys.exc_info()
    _f = _tb.tb_frame
    lineno = _tb.tb_lineno
    filename = _f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, _f.f_globals)
    logging.exception('EXCEPTION IN (%s, LINE %i "%s"): %s', filename, lineno, line.strip(), exc_obj)
