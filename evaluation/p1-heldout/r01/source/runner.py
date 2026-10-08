import subprocess

def run(label):
    return subprocess.run("printf report-" + label, shell=True, capture_output=True)
