# os_concepts/threading_ops.py
# Simulates OS multithreading behavior.
#
# OS Concept: Threads are lightweight units of execution.
# A process (our Flask app) can spawn multiple threads.
# Each thread shares the same memory but runs independently.
# This is how modern OS handles concurrent tasks.

import threading
import time
from database.db import log_activity, get_connection

# A lock prevents two threads from writing to the
# database at the exact same time (race condition prevention)
# This is the OS concept of "mutual exclusion"
db_lock = threading.Lock()


def log_activity_thread(student_id, action):
    """
    Logs activity in a separate background thread.
    The main thread doesn't wait for this to finish.
    """
    def _log():
        # Simulate slight processing delay
        time.sleep(0.1)
        # Acquire lock before writing to database
        with db_lock:
            log_activity(student_id, action)

    thread = threading.Thread(target=_log, daemon=True)
    thread.start()
    return thread


def process_upload_thread(student_id, resource_title, callback=None):
    """
    Processes an upload in a background thread.
    This simulates OS handling file I/O asynchronously.

    daemon=True means this thread dies when the main program exits.
    This is an OS concept — daemon threads run in the background.
    """
    def _process():
        # Simulate file processing time
        time.sleep(0.5)

        with db_lock:
            log_activity(student_id, f"Uploaded: {resource_title}")

        # Update download recommendations in background
        _update_recommendations(student_id)

        if callback:
            callback()

    thread = threading.Thread(target=_process, daemon=True)
    thread.start()
    return thread


def _update_recommendations(student_id):
    """
    Recalculates recommendations after a new upload.
    Runs in background — user doesn't wait for this.
    """
    time.sleep(0.2)
    # In a real app, this would update a recommendations cache
    # For now we just log it
    with db_lock:
        log_activity(student_id, "Recommendations refreshed")


def get_thread_status():
    """
    Returns info about currently active threads.
    Useful for the OS scheduling simulation page.
    """
    active_threads = threading.active_count()
    thread_names   = [t.name for t in threading.enumerate()]
    return {
        'active_count': active_threads,
        'thread_names': thread_names
    }