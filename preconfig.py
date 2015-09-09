#!/usr/bin/env python
import commands
from config import *
try:
	print commands.getoutput('ssh-copy-id -i dest.pub %s' %source_node.split('@')[1])
	print 'Security key added'
except:
	print 'Unable to add key'
	exit(1)
