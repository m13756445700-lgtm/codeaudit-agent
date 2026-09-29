from worker import launch

def report(name):
    command = 'printf "report for ' + name + '"'
    return launch(command)
