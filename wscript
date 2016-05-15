#!/usr/bin/env python3
import os
import sys
from waflib.Task import Task
from waflib import Logs
import subprocess
from distutils.version import LooseVersion, StrictVersion
import imp
import re
import stat
import distutils.spawn

top = "."
out = "build"
src = "src"

def options(ctx):
  ctx.add_option('--prefix', action='store', default="/usr/local", help='install prefix')
  ctx.add_option('--templates', action='store', default="*", help='templates to install')

def checkVersion(name,cmd,regex,requiredVersion,returnCode):
  res = False
  Logs.pprint('WHITE','{0: <40}'.format('Checking {0} version'.format(name)),sep=': ')
  try:
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE,stdout=subprocess.PIPE)
    res = p.communicate()

    line = res[0].decode() + " " + res[1].decode()
    res =  { "returncode": p.returncode, "out":line[0:-1] }
    v = re.match(regex, res["out"])
    if res["returncode"] != returnCode or v == None:
      Logs.pprint('RED','{0} is not available. Cannot continue.'.format(name))
    else:
      version = v.group(1)
      requiredVersionObj = LooseVersion(requiredVersion)
      currentVersionObj = LooseVersion(version)
      if currentVersionObj >= requiredVersionObj:
        Logs.pprint('GREEN',version)
        res = True
      else:
        Logs.pprint('RED','Incorrect version {0} (must be equal or greater than {1}). Cannot continue.'.format(currentVersionObj,requiredVersionObj))
  except Exception as e:
    Logs.pprint('RED','Unable to get version ({0}).'.format(e))
  return res

def checkBinary(name,cmd):
  res = False
  Logs.pprint('WHITE','{0: <40}'.format('Checking {0} version'.format(name)),sep=': ')
  try:
    res = distutils.spawn.find_executable(cmd)
    if res is None:
       Logs.pprint('RED','{0} is not available. Cannot continue.'.format(name))
    else:
       Logs.pprint('GREEN',"present")
  except:
    Logs.pprint('RED','Unable to check binary.')
  return res

def checkPythonModule(moduleName):
  res = False
  Logs.pprint('WHITE','{0: <40}'.format('Checking python module {0}'.format(moduleName)),sep=': ')
  try:
    imp.find_module(moduleName)
    res = True
  except ImportError:
    res = False
  if not res:
    Logs.pprint('RED','{0} python module is not available. Cannot continue'.format(moduleName))
  else :
    Logs.pprint('GREEN',"ok")
    res = True
  return res

def configure(ctx):
  ctx.env.PREFIX = ctx.options.prefix
  if ctx.options.templates == "":
    ctx.env.TEMPLATES = None
  else:
    ctx.env.TEMPLATES = ctx.options.templates.split(",")

  if not checkVersion("Python3",["python3", "--version"],"^Python ([0-9\.]*)$","3.0.0",0):
    ctx.fatal("Missing requirements. Installation will not continue.")  
  if not checkVersion("Python",["python", "--version"],"^ Python ([0-9\.]*)$","2.7.9",0):
    ctx.fatal("Missing requirements. Installation will not continue.")
  if not checkVersion("Ansible",["ansible","--version"],"ansible ([0-9\.]*)","1.9.2",0):
    ctx.fatal("Missing requirements. Installation will not continue.")
  if not checkPythonModule("yaml"):
    ctx.fatal("Missing requirements. Installation will not continue.")
  if not checkPythonModule("progressbar"):
    ctx.fatal("Missing requirements. Installation will not continue.")

def build(ctx):
  sharePath = ctx.path.find_dir('src/share/')
  binPath = ctx.path.find_dir('src/bin/')
  
  ctx.install_files(os.path.join(ctx.env.PREFIX,'share'), sharePath.ant_glob('**/*'), cwd=sharePath, relative_trick=True)
  ctx.install_files(os.path.join(ctx.env.PREFIX,'bin'), binPath.ant_glob('**/*'),  chmod=0655, cwd=binPath, relative_trick=True)
