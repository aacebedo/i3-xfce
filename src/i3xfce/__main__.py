#!/usr/bin/env python3

##########################################################################
# i3-xfce
# Copyright (c) 2014, Alexandre ACEBEDO, All rights reserved.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3.0 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library.
##########################################################################
import re
import os
import sys
import shutil
import pwd
import argparse
import subprocess
import uuid
import time
import signal
import threading
import distutils.spawn
from enum import *
from functools import partial
try:
  from progressbar import AnimatedMarker, Bar, ProgressBar, RotatingMarker, Timer
except Exception as e:
  sys.exit("python3-progressbar is missing")
try:
  import yaml
except Exception as e:
  sys.exit("python3-yaml is missing")


INSTALLDIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))
ROLESDIR = os.path.abspath(os.path.join(INSTALLDIR, "share", "i3-xfce", "roles"))


class RegexedQuestion:
    _question = ""
    _regex = ""
    _options = []
    _default = None
    _error_msg = ""
    _logger = None
    
    def __init__(self, question, error_msg, regex=".*", default=None):
        self._question = question
        self._regex = regex
        self._error_msg = error_msg
        if type(default) is str:
            self._default = default
        else:
            self._default = ""
    
    def ask(self):
        question_tmp = self._question
        if self._default != "":
            question_tmp += " [{0}]".format(self._default)
        v = input(question_tmp + ": ")
        if v == "":
            v = self._default
        if re.match(self._regex, v) :
            return v
        else:
            print("{0}.".format(self._error_msg))
            return RegexedQuestion.ask(self)
        
class BinaryQuestion(RegexedQuestion):
    _question = ""
    _options = None
    
    def __init__(self, question, error_msg, default=None):
        if type(default) is str and re.match("Y|y|N|n", default):
            self._default = default
            
        RegexedQuestion.__init__(self, question + " Y/N", error_msg, "Y|y|N|n", default)
        self._options = {
                         "Y" : self.ok,
                         "y" : self.ok,
                         "N" : self.nok,
                         "n" : self.nok
                         }
    
    def ok(self):
        return True
    
    def nok(self):
        return False
    
    def ask(self):
        v = RegexedQuestion.ask(self)
        return (self._options.get(v))()
      
class StringifiedEnum(Enum):  
  def __str__(self):
    return str(self.value)

class Action(StringifiedEnum):
  INSTALL = "install"
  UNINSTALL = "uninstall"

class ExecutionProgressBar(threading.Thread):

  def __init__(self):
    threading.Thread.__init__(self)
    self.running = False

  def run(self):
    self.running = True
    widgets = [Timer(), " - ", AnimatedMarker()]
    pbar = ProgressBar(widgets=widgets)
        
    while self.running:
      for i in pbar((i for i in range(sys.maxsize))):
        time.sleep(0.1)
        if not self.running:
          return

  def stop(self):
    self.running = False


class CmdLine:

  def __init__(self):
    self.progress_bar = ExecutionProgressBar()

  @staticmethod
  def generate_temp_dir():
    tmp_path = os.path.join("/tmp", str(uuid.uuid1()));
    exists = True
    while exists:
      exists = os.path.exists(tmp_path)
    os.makedirs(tmp_path)
    return tmp_path
  
  @staticmethod
  def install(args):
    CmdLine.perform_action(Action.INSTALL, args)
    
  @staticmethod
  def uninstall(action, args):
    CmdLine.perform_action(Action.UNINSTALL, args)
  
  def execute_action(self, action, args):
    # Get the real user behind the sudo
    username = os.getenv("SUDO_USER")

    if(username == None):
      raise Exception("This program must be ran as root")
    
    additional_options = []
    if args.verbose != False:
      additional_options.append("-vvv")
    if args.dryrun != False:
      additional_options.append("--check")
    tmp_path = CmdLine.generate_temp_dir()
    playbook_path = os.path.join(tmp_path, "i3-xfce.playbook")
    playbook = [{}]
    playbook[0]["hosts"] = "all"
    playbook[0]["roles"] = args.parts
    playbook_file = open(playbook_path, 'w')
    playbook_file.write(yaml.dump(playbook, default_flow_style=False, explicit_start=True))
    playbook_file.close()
    roles_path = os.path.join(ROLESDIR)
    
    ansible_config = open(os.path.join(tmp_path, "ansible.cfg"), "w+")
    ansible_config.write("[defaults]\r\n")
    ansible_config.write("display_skipped_hosts=False\r\n")
    ansible_config.write("roles_path={0}".format(roles_path))
    ansible_config.close()
    command = []
    if len(additional_options) != 0 :
      command = ['ansible-playbook', '-i', 'localhost,', '-e', 'remote_user={}'.format(username), '-e', 'action={}'.format(str(action)), " ".join(additional_options), '-c', 'local', playbook_path]
    else:
      command = ['ansible-playbook', '-i', 'localhost,', '-e', 'remote_user={}'.format(username), '-e', 'action={}'.format(str(action)), '-c', 'local', playbook_path]

    try:
      p = None
      if args.verbose:
        print("Running command: {}".format(" ".join(command)))
        p = subprocess.Popen(command, cwd=os.path.dirname(os.path.realpath(__file__)), env=dict(os.environ, ANSIBLE_CONFIG=os.path.join(tmp_path, "ansible.cfg")))
      else:
        print("Running command: {}".format(" ".join(command)))
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.path.dirname(os.path.realpath(__file__)), env=dict(os.environ, ANSIBLE_CONFIG=os.path.join(tmp_path, "ansible.cfg")))

      self.progress_bar.start()
      p.communicate()
      self.progress_bar.stop()
      self.progress_bar.join()
      if p.returncode != 0:
        if args.verbose:
          raise Exception("Error when executing ansible. Check the ansible logs.")
        else:
          raise Exception("Error when executing ansible. Run i3-xfce again with -v option.")
    except Exception as e:
      raise(e)
    
  @staticmethod
  def parse_args(rawArgs):
    rolesPath = os.path.join(ROLESDIR)
    dirs = os.listdir(rolesPath)
    # Create main parser
    parser = argparse.ArgumentParser(prog="i3-xfce", description='i3-xfce-installer.')
    root_subparsers = parser.add_subparsers(dest="function")
     
    # Parser for list command
    install_parser = root_subparsers.add_parser('install', help='install files')
    install_parser.add_argument('--parts', '-p', help='Parts to install', nargs="+", metavar=dirs, type=str, choices=dirs, default=dirs)
    install_parser.add_argument('--verbose', "-v", help='Verbose mode', action='store_true')
    install_parser.add_argument('--dryrun', "-d", help='Dry run mode', action='store_true')
    
    # Parser for list command
    uninstall_parser = root_subparsers.add_parser('uninstall', help='uninstall files')
    uninstall_parser.add_argument('--parts', '-p', help='Parts to install', nargs="+", metavar=dirs, type=str, choices=dirs, default=dirs)
    uninstall_parser.add_argument('--verbose', "-v", help='Verbose mode', action='store_true')
    uninstall_parser.add_argument('--dryrun', "-d", help='Dry run mode', action='store_true')
     
    return parser.parse_args(rawArgs[1:])
  
  @staticmethod
  def main():
    try:
      res = distutils.spawn.find_executable("ansible")
      if res is None:
        raise Exception("Ansible not found please check your configuration")
      cmdline = CmdLine()
      signal.signal(signal.SIGINT, partial(CmdLine.signal_handler, cmdline))
      args = cmdline.parse_args(sys.argv)
      cmdline.execute_action(args.function, args)
      if(BinaryQuestion("Do you want to reboot your computer now for changes to take effect?",
                             "Enter a Y or a N", "N").ask() == True):
        os.system("reboot now")
      sys.exit()
    except Exception as e:
      sys.exit(e)

  def signal_handler(self, signal, frame):
    self.progress_bar.stop()
    self.progress_bar.join()
    sys.exit(0)

if __name__ == "__main__":
    CmdLine.main()   
