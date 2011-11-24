import mc
import os
import sys
from signal import SIGKILL

webpypid = 0

def runwebpy():
    global webpypid
    webpypid = os.fork()
    if not webpypid:
        #os.execvp(program, (program,) +  args)
        params = mc.Parameters()
        mc.GetApp().RunScript('webserver',params)
    return webpypid #os.wait()[0]

def stopwebpy():
    print "killing process: %d" % webpypid
    os.kill(webpypid,SIGKILL)
    pass

mc.ActivateWindow(14000)



# check with mc.GetWindow(14000) if still running to abort? needs to be in special thread
# call abort function on "uonnload"
