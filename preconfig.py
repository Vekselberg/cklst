#!/usr/bin/env python
import commands
from os import chmod
from config import *
chmod('dest',0400)
try:
	commands.getoutput('ssh-copy-id -i dest.pub %s' %source_node.split('@')[1])
	print 'Security key added on SUT'
	commands.getoutput('ssh-copy-id -i dest.pub %s' %dest_node.split('@')[1])
	print 'Security key added on slave'
except:
	print 'Unable to add key'
	exit(1)
