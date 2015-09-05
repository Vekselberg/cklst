#!/usr/bin/env python
#try:
#	import prlsdkapi
#except:
#	print 'Failed to import Parallels SDK'


import logging, time, commands,hashlib
from config import *
from uuid import uuid4

spacer = lambda x: x + '\n'
sshckbypass='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '

source_node=sshckbypass+source_node
dest_node=sshckbypass+dest_node
def output_w(result):
	with open('results.log', 'a') as file:
		file.write(spacer(result))








def main():
	output_w(source_node)
	output_w(dest_node)
main()
