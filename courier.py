"""
courier: an intelligent subprocessor
"""
import subprocess

class Courier:
    def __init__(self):
        self.cwd = None
    
    def cd(self, cwd):
        self.note('cd ' + cwd)
        self.cwd = cwd
        
    def run(self, *args):
        self.note(' '.join(args))
        p = subprocess.Popen(args, cwd=self.cwd, stdout=subprocess.PIPE)
        self.output(p.stdout.read())
        p.wait()
        return p.returncode
    
    def _store(self, x):
        print x
    
    def note(self, line):
        self._store('$ ' + line)
    
    def output(self, data):
        self._store(data)
