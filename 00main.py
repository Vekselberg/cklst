#!/usr/bin/env python

#try:
#	import prlsdkapi
#except:
#	print 'Failed to import Parallels SDK'


import logging, time, commands, hashlib, re
from config import *
from uuid import uuid4

#host_slicer=lambda x: re.findall(r"[\w^\.]+", x) #i know, it's ugly, host='%s:%s@%s' %(s_root, s_pass, s_host) looks better but regex more interest
host_slicer=lambda x: re.split('[:@]',x)
spacer = lambda x: x + '\n'

sshckbypass='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '
#consts = prlsdkapi.prlsdk.consts
ssh_s_node=sshckbypass+source_node
ssh_d_node=sshckbypass+dest_node

class Halt(Exception):
	pass

def output_w(result):
	with open('results.log', 'a') as file:
		file.write(spacer(result))








def main():
	logging.basicConfig(filename="checklist.log", level=logging.INFO)

	output_w(source_node)
	output_w(dest_node)
	print host_slicer(dest_node) 

if __name__ == "__main__":
	main()
