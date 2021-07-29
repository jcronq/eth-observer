""" Asynchronous Helper Functions """
import time
import asyncio
from functools import (
    wraps
)

from concurrent.futures import ThreadPoolExecutor

thread_pool_executor = ThreadPoolExecutor(64)
async_task_references = set()

def run_in_thread(func):
    """
    Runs the function in a seperate thread so the main thread is not blocked
    """
    loop = asyncio.get_running_loop()
    func_future = loop.run_in_executor(thread_pool_executor, func)
    return func_future

def call_soon(coro):
    """ Call the function soon threadsafe """
    if not asyncio.coroutines.iscoroutine(coro):
        raise RuntimeError("A coroutine is required %s\n hint: you probably want to call this on the result of an non-awaited async function" % coro)

    loop = asyncio.get_running_loop()
    def callback() -> None:
        """Handle the firing of a coroutine."""
        register_ensure_future(coro, loop=loop)

    loop.call_soon_threadsafe(callback)

def register_ensure_future(coro, loop):
    """ Ensures the future is handled """
    task = asyncio.ensure_future(coro, loop=loop)
    async_task_references.add(task)

    # Setup cleanup of strong reference on task completion...
    def _on_completion(_f):
        async_task_references.remove(_f)
    task.add_done_callback(_on_completion)

    return task
