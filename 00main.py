#!/usr/bin/env python

try:
	import prlsdkapi
except:
	print 'Failed to import Parallels SDK\nUnable to continue.\n'
	exit(1)

import logging, time, commands, hashlib, re
from config import *
from uuid import uuid4

#host_slicer=lambda x: re.findall(r"[\w^\.]+", x) #i know, it's ugly, host='%s:%s@%s' %(s_root, s_pass, s_host) looks better but regex more interest
host_slicer=lambda x: re.split('[:@]',x)
spacer = lambda x: x + '\n'

sshckbypass='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '
consts = prlsdkapi.prlsdk.consts
ssh_s_node=sshckbypass+source_node
ssh_d_node=sshckbypass+dest_node

class Halt(Exception):
	pass


def output_w(result):
	with open('results.log', 'a') as file:
		file.write(spacer(result))


def login_server(server, host, user, password, security_level):
	if host=="localhost":
		print 'Test should be runned on remote server'
		raise halt
	else:
		try:
			result = server.login(host, user, password, '', 0, 0,security_level).wait()
		except prlsdkapi.PrlSDKError, e:
			print "Login error: %s" % e
			print "Error code: " + str(e.error_code)
			raise Halt



	login_response = result.get_param()
	product_version = login_response.get_product_version()
	host_os_version = login_response.get_host_os_version()
	host_uuid = login_response.get_server_uuid()
	print ""
	print "Login successful"
	print ""
	print "PCS version: " + product_version
	print "Host OS verions: " + host_os_version
	print "Host UUID: " + host_uuid
	print ""
	print login_response
	print ""



def main():
	logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename="checklist.log", level=logging.INFO)
"""
	#logging.basicConfig(format='%(asctime)s %(levelname)-7s %(filename)s:%(lineno)d %(message)s', level=max(DEBUG, WARNING - args.verbosity * 10))
	output_w(source_node)
	output_w(dest_node)
	print host_slicer(dest_node) 
	logging.info('tst')
"""
	prlsdkapi.init_server_sdk() # Initialize the library.
	server = prlsdkapi.Server() # Create a Server object
 	login_server(server, "mccp6.qa.sw.ru", "root", "1q2w3e", consts.PSL_NORMAL_SECURITY); # and log in to PCS.
	server.logoff() #log ogg 
	prlsdkapi.deinit_sdk() # deinitialize the library.



if __name__ == "__main__":
	main()
