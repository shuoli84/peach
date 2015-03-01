import json
import os
import urllib
import sys
import subprocess
import re
from os.path import expanduser

cookie = 'b6e063a3e2722969a3880ebf89dcd0972dab9667f7b86350'

def get_underlying_command(command):
    paths = os.environ['PATH'].split(':')

    for path in paths:
        command_candidate_path = os.path.join(path, command)
        if os.path.exists(command_candidate_path):
            with open(command_candidate_path, 'r') as f:
                piece = f.read(1024)
                if piece.find(cookie) == -1:
                    return command_candidate_path
    return None

def get_peach_server():
    if 'PEACH_SERVER' in os.environ:
        return os.environ['PEACH_SERVER'] or None

    for setting_file_path in [expanduser("~/.peach.json"), "/etc/peach/conf.json"]:
        if os.path.exists(setting_file_path):
            with open(setting_file_path, 'r') as f:
                setting = json.load(f)
                if 'server' in setting:
                    return setting['server']
    return None

def execute(command):
    command_path = get_underlying_command(command)

    if command_path is None:
        raise RuntimeError('Can not locate %s' % command)

    argv = []
    peach_server = get_peach_server()
    if peach_server is not None:
        for param in sys.argv[1:]:
            if re.match('http', param) is not None:
                argv.append('http://' + peach_server + '?' + urllib.urlencode({"file_url": param}))
            else:
                argv.append(param)
    else:
        argv = sys.argv

    subprocess.call([command_path] + argv)
