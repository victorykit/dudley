"""
courier: an intelligent subprocessor
"""
import subprocess

def execute(*args, **kwargs):
    if kwargs.get('cwd'):
        print '$ cd ' + kwargs['cwd']
    print '$ ' + ' '.join(args)
    kwargs['stdout'] = subprocess.PIPE
    p = subprocess.Popen(args, **kwargs)
    print p.stdout.read()
    p.wait()
