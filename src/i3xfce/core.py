#!/usr/bin/env python2

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
"""
i3-xfce core module
"""

import os
import re
import sys
import argparse
import time
import signal
import threading
import distutils.spawn
from collections import namedtuple
from functools import partial
import logging
import pkg_resources
from enum import Enum

try:
  from ansible import constants as C
  from ansible.parsing.dataloader import DataLoader
  from ansible.vars import VariableManager
  from ansible.inventory import Inventory
  from ansible.playbook.play import Play
  from ansible.executor.task_queue_manager import TaskQueueManager
  from ansible.plugins.callback import CallbackBase
except ImportError:
  sys.exit("ansible package is missing")

try:
  import progressbar
except ImportError:
  sys.exit("progressbar2 package is missing")

import i3xfce.loggers

ROLESDIR = os.path.join(pkg_resources.resource_filename(__name__, 'resources'), "roles")

class RegexedQuestion(object): # pylint: disable=too-few-public-methods
  """
  Class used to ask regexed based question to user
  """

  _question = ""
  _regex = ""
  _options = []
  _default = None
  _error_msg = ""
  _logger = None

  def __init__(self, question, error_msg, regex=".*", default=None):
    """
    Constructor
    """
    self._question = question
    self._regex = regex
    self._error_msg = error_msg
    if isinstance(str, type(default)):
      self._default = default
    else:
      self._default = ""

  def ask(self):
    """
    Asks question to user
    """
    question_tmp = self._question
    if self._default != "":
      question_tmp += " [{}]".format(self._default)
    value = raw_input(question_tmp + ": ") # pylint: disable=bad-builtin
    if value == "":
      value = self._default
    if re.match(self._regex, value):
      return value
    else:
      print "{}.".format(self._error_msg)
      return RegexedQuestion.ask(self)

class BinaryQuestion(RegexedQuestion): # pylint: disable=too-few-public-methods
  """
  Class used to ask binary question to user
  """

  _question = ""
  _options = None

  def __init__(self, question, error_msg, default=None):
    """
    Constructor
    """
    if isinstance(str, type(default)) and re.match("Y|y|N|n", default):
      self._default = default

    RegexedQuestion.__init__(self, question + " Y/N", error_msg, "Y|y|N|n", default)
    self._options = {
        "Y" : True,
        "y" : True,
        "N" : False,
        "n" : False
        }

  def ask(self):
    """
    Asks question to user
    """
    value = RegexedQuestion.ask(self)
    return self._options.get(value)

class StringifiedEnum(Enum): # pylint: disable=too-few-public-methods
  """
  Enum that can be converted to a string
  """

  def __str__(self):
    """
    Convert enum to string
    """
    return str(self.value)

class Action(StringifiedEnum): # pylint: disable=too-few-public-methods
  """
  Operations available in i3-xfce
  """

  INSTALL = "install"
  UNINSTALL = "uninstall"

class TaskExecutionException(Exception):
  """
  Exception raised when a task is not correctly executed
  """

  def __init__(self, msg):
    """
    Constructor
    """
    Exception.__init__(self)
    self._msg = msg

  def __str__(self):
    """
    Convert exception to string
    """
    return self._msg

class TaskCountCallback(CallbackBase):
  """
  Ansible callback used to count tasks
  """

  _total_tasks_num = 0
  _task_name_max_len = 0

  def v2_playbook_on_task_start(self, task, is_conditional):
    """
    Function executed when a task starts
    """
    if task.name != "":
      i3xfce.loggers.ROOTLOGGER.debug("Counted task: %s", task.name)
      self._total_tasks_num = self._total_tasks_num + 1
      if len(task.name) > self._task_name_max_len:
        self._task_name_max_len = len(task.name)

  def get_total_tasks_num(self):
    """
    Get the total number of tasks being executed
    """
    return self._total_tasks_num

  def get_task_name_max_len(self):
    """
    Get the maximum length of the name between each tasks being executed
    """
    return self._task_name_max_len

class ExecutionProgressBar(threading.Thread):
  """
  Class representing a progressbar
  """

  def __init__(self, steps_nb, step_name_len):
    """
    Constructor
    """
    threading.Thread.__init__(self)
    self._running = False
    self._current_step = 0
    self._steps_nb = steps_nb
    self._step_name_len = step_name_len + len(str(steps_nb)) * 2 + 2
    self._widgets = [" ".ljust(self._step_name_len),
                     ' [', progressbar.Timer(), '] ',
                     progressbar.Bar(),
                     ' (', progressbar.ETA(), ') ',
                    ]
    self._pbar = progressbar.ProgressBar(max_value=steps_nb, widgets=self._widgets)

  def run(self):
    """
    Run thread body
    """
    self._running = True
    while self._running:
      self._pbar.update(self._current_step)
      time.sleep(0.1)
      if not self._running:
        return

  def stop(self):
    """
    Stop thread
    """
    self._running = False

  def increment_step(self, name=None):
    """
    Increment current step
    """
    self._current_step = self._current_step + 1
    if name != None:
      self._widgets[0] = "{}/{} {}".format(str(self._current_step).zfill(len(str(self._steps_nb))),
                                           self._steps_nb, name.ljust(self._step_name_len))
    time.sleep(1)

class PlaybookExecutionCallback(CallbackBase):
  """
  Ansible callback executed for real playbook execution
  """

  _pbar = None
  _task_failed = False

  def __init__(self, total_tasks_num, task_name_max_len):
    """
    Constructor
    """
    CallbackBase.__init__(self)
    self._pbar = ExecutionProgressBar(total_tasks_num, task_name_max_len)

  def v2_runner_on_ok(self, result):
    """
    Function executed when a task is completed
    """
    i3xfce.loggers.ROOTLOGGER.debug("Task '%s' completed", result._task.get_name()) # pylint: disable=protected-access

  def v2_runner_on_skipped(self, result):
    """
    Function executed when a task is skipped
    """
    i3xfce.loggers.ROOTLOGGER.warn("Task '%s' skipped", result._task.get_name()) # pylint: disable=protected-access

  def v2_runner_on_failed(self, result, ignore_errors=False):
    """
    Function executed when a task fails
    """
    i3xfce.loggers.ROOTLOGGER.error("Task '%s' failed: %s", result._task.get_name(), # pylint: disable=protected-access
                                    result._result["msg"]) # pylint: disable=protected-access
    self._task_failed = True

  def v2_playbook_on_play_start(self, play):
    """
    Function executed when the playbook starts
    """
    i3xfce.loggers.ROOTLOGGER.debug("Playbook is started")
    self._pbar.start()

  def v2_playbook_on_task_start(self, task, is_conditional):
    """
    Function executed when a task starts
    """
    if task.name != "":
      self.get_progress_bar().increment_step(task.get_name())

  def get_progress_bar(self):
    """
    Progressbar getter
    """
    return self._pbar

  def get_task_failed(self):
    """
    Get if task of the playbook has failed
    """
    return self._task_failed

class CmdLine(object):
  """
  Main command line class
  """

  _results_callback = None

  @staticmethod
  def _execute_play(play_source, inventory, var_mgr, loader, options, callback):  # pylint: disable=too-many-arguments
    """
    Execute the playbook
    """
    play = Play().load(play_source, variable_manager=var_mgr, loader=loader)
    tqm = None
    try:
      tqm = TaskQueueManager(
          inventory=inventory,
          variable_manager=var_mgr,
          loader=loader,
          options=options,
          passwords=None,
          stdout_callback=callback,
          )
      _ = tqm.run(play)
    except Exception as exc:
      raise TaskExecutionException(str(exc))
    finally:
      if tqm is not None:
        tqm.cleanup()

  def execute_action(self, action, args):
    """
    Execute the requested operation
    """
    C.DEFAULT_ROLES_PATH = [os.path.join(ROLESDIR, str(action))]

    i3xfce.loggers.ROOTLOGGER.debug("Executing the %s action", action)
    # Get the real user behind the sudo
    username = os.getenv("SUDO_USER")

    if username is None:
      i3xfce.loggers.ROOTLOGGER.debug("Unable to get SUDO_USER environment variable. This means i3-xfce has not been \
      started using sudo")
      raise Exception("This program must be ran using sudo ")

    i3xfce.loggers.ROOTLOGGER.debug("Creating the option tuple")
    options_tuple = namedtuple('Options', ['connection', 'forks', 'module_path', 'become_user', 'become',
                                           'become_method', 'check', 'verbosity'])
    try:
      # initialize needed objects
      variable_manager = VariableManager()
      variable_manager.extra_vars = dict(action=str(action),
                                         remote_user=username)

      loader = DataLoader()
      i3xfce.loggers.ROOTLOGGER.debug("Creating option to count number of tasks to execute")
      options = options_tuple(connection=None, module_path=None, forks=1, become_user=None,
                              become=None, become_method=None, verbosity=0, check=True)
      tasks_count_callback = TaskCountCallback()
      # create inventory and pass to var manager
      inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=None)
      variable_manager.set_inventory(inventory)
      # create play with tasks
      play_source = dict(
          name="Ansible Play",
          hosts='localhost',
          gather_facts='no',
          ignore_errors="yes",
          roles=args.parts
          )
      CmdLine._execute_play(play_source, inventory, variable_manager, loader, options, tasks_count_callback)

      i3xfce.loggers.ROOTLOGGER.debug("%i tasks are going to be executed", tasks_count_callback.get_total_tasks_num())
      play_source["ignore_errors"] = "no"
      options = options_tuple(connection=None, module_path=None, forks=1, become_user=None, become=None,
                              become_method=None, verbosity=0, check=args.dryrun)
      self._results_callback = PlaybookExecutionCallback(tasks_count_callback.get_total_tasks_num(),
                                                         tasks_count_callback.get_task_name_max_len())
      CmdLine._execute_play(play_source, inventory, variable_manager, loader, options, self._results_callback)

      self._results_callback.get_progress_bar().stop()
      self._results_callback.get_progress_bar().join()

      if self._results_callback.get_task_failed() is True:
        raise TaskExecutionException("")
    except TaskExecutionException as exc:
      raise
    except Exception as exc:
      raise TaskExecutionException(str(exc))

  @staticmethod
  def parse_args(raw_args):
    """
    Parse arguments
    """
    dirs = os.listdir(os.path.join(ROLESDIR, "install"))
    # Create main parser
    parser = argparse.ArgumentParser(prog="i3-xfce", description='i3-xfce-installer.')
    parser.add_argument("--version", "-v", help="Display version", action='version',
                        version="{}".format(pkg_resources.require("i3-xfce")[0].version))
    root_subparsers = parser.add_subparsers(dest="function")

    # Parser for list command
    install_parser = root_subparsers.add_parser('install', help='install files')
    install_parser.add_argument('--parts', '-p', help='Parts to install', action="append", metavar=dirs,
                                type=str, choices=dirs)
    install_parser.add_argument('--verbose', help='Verbose mode', action='store_true', default=False)
    install_parser.add_argument('--dryrun', "-d", help='Dry run mode', action='store_true', default=False)

    # Parser for list command
    uninstall_parser = root_subparsers.add_parser('uninstall', help='uninstall files')
    uninstall_parser.add_argument('--parts', '-p', help='Parts to install', action="append", metavar=dirs, type=str,
                                  choices=dirs)
    uninstall_parser.add_argument('--verbose', help='Verbose mode', action='store_true', default=False)
    uninstall_parser.add_argument('--dryrun', "-d", help='Dry run mode', action='store_true', default=False)

    res = parser.parse_args(raw_args[1:])
    if res.parts is None:
      res.parts = dirs
    return res

  def signal_handler(self, *_):
    """
    Handler called when ctrl-c is pressed
    """
    if self._results_callback != None:
      self._results_callback.get_progress_bar().stop()
    sys.exit(0)

def main():
  """
  Main function
  """
  i3xfce.loggers.init_loggers()

  try:
    res = distutils.spawn.find_executable("ansible")
    if res is None:
      raise Exception("Ansible not found please check your configuration")
    cli = CmdLine()
    signal.signal(signal.SIGINT, partial(cli.signal_handler, cli))
    args = cli.parse_args(sys.argv)

    if args.function != None:
      if args.verbose is True:
        i3xfce.loggers.set_log_level(logging.DEBUG)
      else:
        i3xfce.loggers.set_log_level(logging.INFO)

      res = cli.execute_action(args.function, args)

      if(BinaryQuestion("Do you want to reboot your computer now for changes to take effect?",
                        "Enter a Y or a N", "N").ask() is True):
        os.system("reboot now")
    else:
      cli.parse_args([None, "-h"])
    sys.exit()
  except Exception as exc:  # pylint: disable=broad-except
    i3xfce.loggers.ROOTLOGGER.error("A task failed to execute, check the messages and correct \
the issue before restarting i3-xfce")
    sys.exit(exc)
