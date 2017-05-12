# -*- coding: utf-8 -*-

import logging
import consts
import subprocess
import re
import shlex

log = logging.getLogger('utils')


def get_dsMenu_version(versionfile = consts.VERSION_FILE):
    try:
        with open(versionfile, 'r') as f:
            return f.read().strip()
    except IOError:
        log.error("set dsmenu version from %s fail" % versionfile)
        return ""

def run_cmd(cmd, is_file=False, *input_list):
    if is_file is False:
        cmd = shlex.split(cmd)
    # run cmd with the current user
    if is_file is False:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    else:
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    input_str = None
    if len(input_list)>0:
        input_str = ''
        for ipt in input_list:
            input_str = input_str + ipt +"\n"

    stdout, stderr = p.communicate(input_str)
    return_code = p.wait()
    return return_code, stdout, stderr

def get_line_by_head(filename, head):
    infile = open(filename)
    line = infile.readline()
    while line:
        if re.match(r"%s:"%head, line):
            return line
        line = infile.readline()

    return ""
