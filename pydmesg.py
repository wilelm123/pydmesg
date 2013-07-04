#!/usr/bin/python
#
'''
    This script transfer the dmesg timestamp to human-readable time format
    Just simply wrappered the dmesg command,hope you like it! :)
'''
import sys
import re
import time
import optparse
import commands
import logging
import inspect
from termcolor import colored,cprint

def lineno():
   return inspect.currentframe().f_back.f_lineno

def debug(msg,lineno):
    if options.debug:
        print(colored("[DEBUG] (%d) %s" % (lineno,msg),'blue',attrs=['underline']))

def get_dmesg_log():
    cmd='dmesg'
    if options.clear:
        cmd+=' -c'
    if options.raw:
        cmd+=' -r '
    if options.buffer:
        cmd+=' -s %s ' % options.buffer
    if options.level:
        cmd+=' -n %s ' % options.level    
    timeout=10
    line_cache=list()
    p_ret,p_out=commands.getstatusoutput(cmd)
    if p_ret != 0:
        cprint('Attention!command %s run error.' % (cmd),'red',attrs=['bold'])
        sys.exit(2)
    lines=p_out.splitlines()
    for line in lines:
        debug("The line value: %s" % line,lineno())
        m=re.match(r'\[\s*(\d+)\.(\d+)\s*\](.*)',line)
        debug("The m value: %s" % m,lineno())
        if m is not None:
            line_cache.append("[%s] %s" % (time_transfer(m.group(1)),kw_highlight(m.group(3))))
    return line_cache

def time_transfer(dmesg_time):
    with open('/proc/uptime') as up:
        content=up.read()
        debug("The uptime content value: %s" % content,lineno())
        if content is not None:
            uptime=content.split()[0]
            idle_time=content.split()[1]
            debug("The uptime value: %s" % uptime,lineno())
            debug("The idle_time value: %s" % idle_time,lineno())
        else:
            uptime=0
            idle_time=0
    time_zone_diff=8*3600
    now=time.time()
    debug("The now time value %s" % str(now),lineno())
    dtime=float(now)-float(uptime)+float(dmesg_time)+time_zone_diff # +float(idle_time)
    debug("The dtime value: %f" % dtime,lineno())
    dtime=time.gmtime(dtime)
    formatted_time=time.strftime('%Y/%m/%d %H:%M:%S',dtime)
    debug("The formatted time value: %s" % str(formatted_time),lineno())
    return formatted_time

def kw_highlight(line):
    kw=options.key
    if kw is not None:
        kw_list=kw.split(',')
    else:
        return line
    hl=line
    for k in kw_list:
        hw=colored(k.lower(),'green',attrs=['bold','underline'])
        if options.ignore:
            rep=re.compile(r'%s' % k,re.I)
            hl=rep.sub(hw,hl)
        else:
            rep=re.compile(r'%s' % k)
            hl=rep.sub(hw,hl)
            
    return hl

def get_other_log(cmd):
    line_cache=list()
    if cmd:
        p_ret,p_out=commands.getstatusoutput(cmd)
        if p_ret != 0:
            cprint('Attention!command %s run error.' % (cmd),'red',attrs=['bold'])
            sys.exit(2)
        lines=p_out.splitlines()
        for line in lines:
            line_cache.append(kw_highlight(line))
        return line_cache
    else:
        return None

def parse_param():
    description='''This script transfer the dmesg timestamp to human-readable time format.
                   Default search the lines with key word error.
                                Just simply wrappered the dmesg command.
                                Author: Wilelm (chen lei)

 hope you like it! :)
'''
    parser=optparse.OptionParser(
        description=description,
        usage='%prog [options] <args>',
        version='0.1')
    parser.add_option('-r','--regexp',action='store',dest='reg',default=None,
        help='The key word pattern to search,default:None')
    parser.add_option('-c','--color',action='store',dest='color',
        type='choice',choices=['green','yellow','blue'],default='yellow',
        help='Print the key word you search with this colored background,default:yellow')
    parser.add_option('-o','--only',action='store_true',default=False,dest='only',
        help='When search the regexp matched pattern,only print the matched line,not avaliable with -k option,default:False')
    parser.add_option('-d','--debug',action='store_true',default=False,dest='debug',
        help='Turn on the debug mode')
    parser.add_option('-C','--cmd',action='store',dest='cmd',default=None,
        help='The command that could provide logs to format,default:None')
    parser.add_option('-k','--key',action='store',dest='key',default=None,
        help='Highlight the key words,separate with comma,default:None')
    parser.add_option('-i','--ignorecase',action='store_true',default=False,dest='ignore',
        help='When searching pattern,ignore the case,default:False')
    o_parser=optparse.OptionGroup(
        parser,'Dmesg original options',
        'When both options are used, only the last option on the command line will have an effect.')
    o_parser.add_option('--clear',action='store_true',default=False,dest='clear',
        help='Origin: -c . Clear the ring buffer contents after printing.')
    o_parser.add_option('--raw',action='store_true',default=False,dest='raw',
        help='Origin: -r . Print the raw message buffer, i.e., don\'t strip the log level prefixes.')
    o_parser.add_option('--buffersize',action='store',default=None,dest='buffer',
        help="Origin: -s . Use a buffer of size bufsize to query the kernel ring buffer.  This is 16392 by default.")
    o_parser.add_option('--level',action='store',default=None,dest='level',
        help="Origin: -n . Set the level at which logging of messages is done to the console.") 
    parser.add_option_group(o_parser)
    options,args=parser.parse_args()
    return options

def display_logs(logs):
    for line in logs:
        r_custom=None
        r_err=re.compile(r'error',re.IGNORECASE)
        if options.ignore:
            if options.reg:
                r_custom=re.compile(r'%s' % options.reg,re.I)
        else:
            if options.reg:
                r_custom=re.compile(r'%s' % options.reg)
            
        if r_custom:
            if r_custom.search(line):
                if options.color:
                    cprint(line,options.color,attrs=['bold'])
                    continue
                else:
                    print("%s" % line)
                    continue
        if r_err.search(line):
            cprint(line,'red',attrs=['bold'])
        else:
           if not options.only:
               print(line)
           else:
               pass

def main():
    dmesg_log=get_dmesg_log()
    if not options.cmd:
        display_logs(dmesg_log)
    elif options.cmd.strip() == 'dmesg':
        display_logs(dmesg_log)
    else:
        other_log=get_other_log(options.cmd)
        display_logs(other_log)
        
        
    
         
if __name__ == '__main__':
    options=parse_param()
    main()
