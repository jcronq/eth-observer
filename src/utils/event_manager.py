""" manager for events and their subscriptions"""
import asyncio
from typing import (
    Mapping,
    List,
    Callable,
    NewType,
    Union
)
from datetime import datetime, timedelta
from .logger import print_exception

from ._async import async_loop

ON_UPDATE_INTERVAL = 10 # seconds
HIGH_FREQ_TIMER_INTERVAL = 0.1 # seconds
# LOW_FREQ_TIMER_INTERVAL is currently unused.  The idea here is that we create
# a second loop that loops at a slower frequency, which moves timers to the HIGH_FREQUENCY_TIMER
# only if they are about to expire.  This way we keep the number of timers being checked frequently
# to a minimum while ensuring high precision for all timers.
LOW_FREQ_TIMER_INTERVAL = 10 # seconds

StateCallback = NewType('StateCallback', Callable[[str, dict, dict], None])
EventCallback = NewType('EventCallback', Callable[[None], None])
Callback = NewType('Callback', Union[StateCallback, EventCallback])
EventMap = NewType('EventMap', Mapping[str, List[Callback]])

class EventManager:
    """ manager for events and their subscriptions"""
    subscriptions: Mapping[str, EventMap]
    _update_loop: asyncio.Task
    _running: bool

    def __init__(self, app):
        self.subscriptions = {
            'on_class_event': {},
            'on_event': {},
            'timers': []
        }
        self._update_loop = None
        self._timer_loop = None
        self._running = False
        startup_wrapper = app.on_event('startup')
        startup_wrapper(self._app_startup)
        shutdown_wrapper = app.on_event('shutdown')
        shutdown_wrapper(self._app_shutdown)

    async def _app_startup(self):
        await self.publish_on_event('startup')
        self._running = True
        self._update_loop = asyncio.create_task(self._on_update())
        self._timer_loop = asyncio.create_task(self._on_timer_check())

    async def _app_shutdown(self):
        self._running = False
        await self._update_loop
        await self._timer_loop
        await self.publish_on_event('shutdown')

    @async_loop(interval=ON_UPDATE_INTERVAL)
    async def _on_update(self):
        if self._running:
            print("update_loop")
            await self.publish_on_event('on_update')
        return self._running

    @async_loop(interval=HIGH_FREQ_TIMER_INTERVAL)
    async def _on_timer_check(self):
        if self._running:
            await self._handle_timer_expiry()
        return self._running

    async def _handle_timer_expiry(self):
        now = datetime.utcnow()
        expired_timers = []
        for timer in self.subscriptions['timers']:
            if timer['expiration_time'] < now:
                await timer['callback']()
                expired_timers.append(timer)

        for timer in expired_timers:
            self.remove_timer(timer)

    def add_timer(self, duration: timedelta, callback):
        """ Schedules the callback to be executed at a specific time """
        now = datetime.utcnow()
        timer_obj = {
            'expiration_time': now + duration,
            'callback': callback
        }
        self.subscriptions['timers'].append(timer_obj)
        return timer_obj

    def remove_timer(self, timer_obj):
        """ Schedules the callback to be executed at a specific time """
        self.subscriptions['timers'].remove(timer_obj)

    async def publish_on_event(self, event_name: str):
        """ publish the event to subscribers """
        if '.' in event_name:
            [class_type, event_id] = event_name.split('.')
            await self.publish_on_class_event(class_type, event_id)
        on_event_subscriptions = [event for event in self.subscriptions['on_event'].get(event_name, [])]
        print('on_event', event_name, f"{len(on_event_subscriptions)} Subscriptions")
        for _i, callback in enumerate(on_event_subscriptions, start=1):
            try:
                await callback()
            except Exception:
                msg = f"Subscription: {_i}/{len(on_event_subscriptions)}"
                print('subscription_failure', 'on_event', event_name, msg)
                print_exception()

    async def publish_on_class_event(self, class_type: str, event_id: str):
        """ publish the event to subscribers """
        on_event_subscriptions = [event for event in self.subscriptions['on_class_event'].get(class_type, [])]
        print('on_class_event', class_type, f"{len(on_event_subscriptions)} Subscriptions")
        for _i, callback in enumerate(on_event_subscriptions, start=1):
            try:
                await callback(event_id)
            except Exception:
                msg = f"Subscription: {_i}/{len(on_event_subscriptions)}"
                print('subscription_failure', 'on_class_event', class_type, msg)
                print_exception()

    def subscribe(self, subscription_type: str, subscription_key: str, callback: Callback) -> None:
        """ Subscribe to events by subscription_type ex) entity_id, entity_domain """
        self.subscriptions[subscription_type].setdefault(subscription_key, []).append(callback)
        print('subscribe', subscription_type, subscription_key, f"{len(self.subscriptions[subscription_type][subscription_key])} Subscriptions")


    def subscribe_on_event(self, event: str, callback: EventCallback) -> None:
        """ Subscribe to events by entity_domain """
        self.subscribe('on_event', event, callback)

    def subscribe_on_class_event(self, event_class: str, callback: EventCallback) -> None:
        """ Subscribe to events by entity_domain """
        self.subscribe('on_class_event', event_class, callback)
