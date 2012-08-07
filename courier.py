"""
courier: an intelligent subprocessor
"""
import sys, subprocess

class Courier:
    def __init__(self, storer=None):
        self.cwd = None
        if storer: self._store = storer
    
    def cd(self, cwd):
        self.note('cd ' + cwd)
        self.cwd = cwd
        
    def run(self, *args):
        self.note(' '.join(args))
        p = subprocess.Popen(args, cwd=self.cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.output(p.stderr.read())
        self.output(p.stdout.read())
        p.wait()
        return p.returncode
    
    def _store(self, x):
        sys.stdout.write(x)
    
    def note(self, line):
        self._store('$ ' + line + '\n')
    
    def output(self, data):
        self._store(data)
