#!/usr/bin/python

import ConfigParser
import argparse
import logging
import logging.handlers
import os
import re
import sys

def get_match_from_binary(pattern, data):
    reg = re.compile(pattern)
    if (reg.search(data)):
        return True
    else:
        return False

def check_binary(file):
    try:
        data = open(file, 'r').read(1000)
        if '\0' in data:
            return get_match_from_binary(opts.PATTERN, data)
    except IOError:
        return False
    
def get_lines_from_file(file):
        try:
            lines = [i for i in open(file, 'r').read().split('\n')]
            return lines
        except IOError:
            pass

def recurse(dir):
    temp_files = []
    for dirname, dirnames, filenames in os.walk(dir):
        for filename in filenames:
            temp_files.append(os.path.join(dirname, filename))
    return temp_files

def get_match_from_lines(pattern, lines, ln_flag, ig_flag):
    s_r = []
    if ig_flag:
        reg = re.compile(pattern, flags=re.IGNORECASE)
    else:
        reg = re.compile(pattern)
    e_lines = enumerate(lines,start=1)
    for ln, line in e_lines:
        if(reg.search(line)):
            if ln_flag is True:
                s_r.append(str(ln) + ":" + line)
            else:
                s_r.append(line)
    return s_r

def display(files, ln_flag=False, ig_flag=False):
    if not files:
        lines = [line for line in sys.stdin.read().split('\n')]
        result = get_match_from_lines(opts.PATTERN, lines, ln_flag, ig_flag)
        for i in result:
            info_logger.info(i)
    else:
        for f in files:
            if os.path.isfile(f):
                if check_binary(f):
                    info_logger.info('Binary file ' + f + ' matches')
                else:
                    lines = get_lines_from_file(f)
                    result = get_match_from_lines(opts.PATTERN, lines, ln_flag, ig_flag)
                    for i in result:
                        info_logger.info(f + ":" + i)

def options(opts):
    result = []
    if opts.n and opts.i:
        display(opts.FILE, ln_flag=True, ig_flag=True)

    elif opts.n:
        display(opts.FILE, ln_flag=True)

    elif opts.r:
        files = []
        for f in opts.FILE:
            if os.path.isdir(f):
                files.extend(recurse(f))
            else:
                files.append(f)
        display(files)

    elif opts.binary:
        display(opts.FILE)
        
    else:
        display(opts.FILE)

def config_file_parse(command_opts):
    """Must give the command line options first priority"""

    conf_parser = ConfigParser.SafeConfigParser()
    try:
        conf_parser.read('grep.ini')
        if not command_opts.n:
            command_opts.n = conf_parser.getboolean('default_options', 'with_line_num')
        if not command_opts.i:
            command_opts.i = conf_parser.getboolean('default_options', 'with_ignore_case')
        if not command_opts.r:
            command_opts.r = conf_parser.getboolean('default_options', 'with_recursive')
    except (ConfigParser.NoSectionError, ConfigParser.ParsingError
            , ConfigParser.NoOptionError) as e:
        debug_logger.error(('Unable to parse config {file}: Error: ').format(
            file='grep.ini') + str(e))
    return command_opts

if __name__ == '__main__':

    log_file = os.environ['HOME'] + '/grep.log'
    debug_logger = logging.getLogger('debug_logger')
    info_logger = logging.getLogger('info_logger')

    #debug logger for writing to file
    debug_logger.setLevel(logging.DEBUG)

    #info logger for printing to STDOUT
    info_logger.setLevel(logging.INFO)

    # define a handler to log to a file
    handler = logging.handlers.TimedRotatingFileHandler(log_file, when='d', interval=1
            , backupCount=7)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    debug_logger.addHandler(handler)
    info_logger.addHandler(handler)
    
    #define default stream handler to write output to screen
    bf = logging.Formatter()
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(bf)
    info_logger.addHandler(sh)
    
    debug_logger.debug(str(sys.argv[:]))
    try:
        parser = argparse.ArgumentParser(version='0.2')
        parser.add_argument('-n', help="print with line numbers", action="store_true")
        parser.add_argument('-i', help="ignore case", action="store_true")
        parser.add_argument('-r', help="recursive", action="store_true")
        parser.add_argument('--binary', help="Search in Binary files", action="store_true")
        parser.add_argument('PATTERN', action="store")
        parser.add_argument('FILE', nargs="*")
        opts = parser.parse_args()
        opts = config_file_parse(opts)
        options(opts)
    except KeyboardInterrupt:
        print 'KeyboardInterrupt'

#vim: set ft=python ts=4 sw=4 sts=4 et :
