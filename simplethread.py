"""
simplethread: threading for humans
"""
import threading, Queue as qmodule

def spawn(func, daemon=True):
    t = threading.Thread(target=func)
    t.daemon = daemon
    t.start()

class Queue(qmodule.Queue):
    def get(self, timeout=0):
        return qmodule.Queue.get(self, bool(timeout), timeout)

Empty = qmodule.Empty
