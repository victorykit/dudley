"""
simplethread: threading for humans
"""
import threading

def spawn(func, daemon=True):
    t = threading.Thread(target=func)
    t.daemon = daemon
    t.start()