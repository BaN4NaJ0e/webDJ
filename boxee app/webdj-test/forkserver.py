import os
import sys
import time
from signal import SIGTERM

pid = 0

def run(program, *args):
    global pid
    pid = os.fork()
    if not pid:
        os.execvp(program, (program,) +  args)
    return pid #os.wait()[0]

run("python2.4", "webserver.py")
print "running server with pid: " + str(pid)
time.sleep(5)
print "killing webserver"
os.kill(pid,SIGTERM)
print "done"