#!/usr/bin/env python
import commands
from os import chmod
from config import *
chmod('dest',0400)
try:
	commands.getoutput('ssh-copy-id -i dest.pub %s' %source_node.split('@')[1])
	print 'Security key added on SUT'
	if dest_node !='':
		commands.getoutput('ssh-copy-id -i dest.pub %s' %dest_node.split('@')[1])
		print 'Security key added on slave'
	else:
		print 'No slave node provided'
except:
	print 'Unable to add key'
	exit(1)
