"""
utils:
- provides utility wrappers to run asynchronous functions in a blocking environment.
- vendor functions from ipython_genutils that should be retired at some point.
"""
import asyncio
import inspect
import os

def run_sync(coro):
    def wrapped(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Workaround for bugs.python.org/issue39529.
            try:
                loop = asyncio.get_event_loop_policy().get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        import nest_asyncio  # type: ignore

        nest_asyncio.apply(loop)
        future = asyncio.ensure_future(coro(*args, **kwargs), loop=loop)
        try:
            return loop.run_until_complete(future)
        except BaseException as e:
            future.cancel()
            raise e

    wrapped.__doc__ = coro.__doc__
    return wrapped