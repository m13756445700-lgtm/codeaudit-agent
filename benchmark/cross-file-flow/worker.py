import subprocess

def launch(command):
    return subprocess.check_output(['/bin/sh', '-c', command], text=True)
