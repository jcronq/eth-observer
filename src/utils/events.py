""" Events and Stuff """
import asyncio
import functools
import logging

import utils._async as _async

global_events = {}

logger = logging.getLogger("events")

def global_event(event_name):
    """ Register a function to be called when global event 'event_name' is triggered """
    def global_event_wrapper(func):
        global_events.setdefault(event_name, []).append(func)

        functools.wraps(func)
        async def global_event_func(*args, **kwargs):
            func(*args, **kwargs)
        return global_event_func

    return global_event_wrapper

def trigger_global_event(event_name, *args, **kwargs):
    """ Trigger all events registered to the global name 'event_name' """
    for event in global_events.get(event_name, []):
        _async.call_soon(event(*args, **kwargs))

def subscribe_to_global_event(event_name, func):
    """ Register a function to be called when global event 'event_name' is triggered """
    global_events.setdefault(event_name, []).append(func)

async def run():
    while(True):
        trigger_global_event('on_update')
        await asyncio.sleep(30)
