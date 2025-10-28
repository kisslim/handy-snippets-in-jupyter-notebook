import multiprocessing as mp
import queue
import time
from typing import Any, Generator, Iterator

class TimeoutException(Exception):
    """Exception raised when a generator times out"""
    pass

def _generator_worker(generator: Iterator[Any], output_queue: mp.Queue, done_event: mp.Event) -> None:
    """Worker function that runs the generator in a separate process"""
    try:
        for item in generator:
            if done_event.is_set():
                break
            output_queue.put(('item', item))
        output_queue.put(('done', None))
    except Exception as e:
        output_queue.put(('error', e))
    finally:
        # Signal that we're done
        output_queue.put(('finished', None))

def timeout_wrapper(generator: Generator[Any, None, None], timeout_seconds: float, quiet: bool = False) -> Generator[Any, None, None]:
    """
    Wrap a generator with timeout functionality.
    
    Args:
        generator: The generator to wrap
        timeout_seconds: Timeout in seconds for each next() call
        quiet: If True, stop iteration on timeout; if False, raise TimeoutException
    
    Yields:
        Items from the wrapped generator
    
    Raises:
        TimeoutException: If timeout occurs and quiet=False
    """
    output_queue = mp.Queue()
    done_event = mp.Event()
    
    # Start the generator in a separate process
    process = mp.Process(
        target=_generator_worker,
        args=(generator, output_queue, done_event),
        daemon=True
    )
    process.start()
    
    try:
        while process.is_alive() or not output_queue.empty():
            try:
                # Get item with timeout
                msg_type, content = output_queue.get(timeout=timeout_seconds)
                
                if msg_type == 'item':
                    yield content
                elif msg_type == 'done':
                    break
                elif msg_type == 'error':
                    raise content
                elif msg_type == 'finished':
                    break
                    
            except queue.Empty:
                # Timeout occurred
                if quiet:
                    break
                else:
                    raise TimeoutException(f"Generator timed out after {timeout_seconds} seconds")
    
    finally:
        # Signal the worker to stop and clean up
        done_event.set()
        process.terminate()
        process.join(timeout=1.0)
        if process.is_alive():
            process.kill()
        
        # Clean up the queue
        while not output_queue.empty():
            try:
                output_queue.get_nowait()
            except queue.Empty:
                break