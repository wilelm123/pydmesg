#!/usr/bin/python
#

from __future__ import division
import os
import sys
import re
import time
import urllib2
import signal
import subprocess
import traceback
import optparse
import glob
from subprocess import Popen,PIPE

__author__ = 'gongxiangfeng@jike.com (Chris)'

def pyShell(cmd,timeout=None):
    p_out=''
    p_err=''
    p_ret=0
    p=subprocess.Popen(cmd,shell=True,close_fds=True,preexec_fn=os.setsid,stdout=PIPE,stderr=PIPE)
    if not timeout:
        p_ret=p.wait()
    else:
        fin_time=time.time()+timeout
        while p.poll() == None and fin_time > time.time():
            time.sleep(0.1)
        if fin_time <= time.time():
            try:
                p_err="%s:process run timeout" % cmd
                os.killpg(p.pid(),signal.SIGKILL)
            except OSError as err:
                if DEBUG:
                    traceback.print_exc()
                p_err="%s:kill sub process failed,%r" % (cmd,repr(err))

        p_ret=p.returncode
    if not p_err:
        p_out,p_err = p.communicate()

    try:
        p.stdout.close()
        p.stderr.close()
    except:
        if DEBUG:
            traceback.print_exc()
        pass
    result=(p_out,p_err,p_ret)
    return result


