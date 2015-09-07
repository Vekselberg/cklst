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
	logging.info('[SUT] PCS: %s, Host OS ver: %s Host UUID: %s' %(product_version, host_os_version, host_uuid))


def add_net_adapter(srv, vm):
	srv_config = srv.get_srv_config().wait().get_param()
	net_adapter = srv_config.get_net_adapter(0)
	try:
		vm.begin_edit().wait()
	except prlsdkapi.PrlSDKError, e:
		print "Error: %s" % e
		return
	net = vm.create_vm_dev(consts.PDE_GENERIC_NETWORK_ADAPTER)
	net.set_virtual_network_id('Bridged')
	net.set_configure_with_dhcp(True)
	net.set_enabled(True)
	net.set_bound_adapter_index(net_adapter.get_sys_index())
	net.set_bound_adapter_name(net_adapter.get_name())
	try:
		vm.commit().wait()
	except prlsdkapi.PrlSDKError, e:
		print "Error: %s" % e
		return 


def create_ct(server):
	name='CentOs_%s' %uuid4().hex[:10]
	ct = server.create_vm()
	ct.set_vm_type(consts.PVT_CT)
	ct.set_name(name)
	ct.set_os_template('centos-6-x86_64')
	ct.set_ram_size(2048)

	print "Creating a virtual server..."
	try:
		ct.reg("", True).wait()
	except prlsdkapi.PrlSDKError, e:
		print "Error: %s" % e
		return
	logging.info('CT %s Created.' %name)
	print "Parallels Container %s was created successfully." %name
	add_net_adapter(server, ct)




def main():
	logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename="checklist.log",filemode='w', level=logging.INFO)
	prlsdkapi.init_server_sdk() # Initialize the library.
	server = prlsdkapi.Server() # Create a Server object
 	login_server(server, host_slicer(source_node)[2], host_slicer(source_node)[0], host_slicer(source_node)[1], consts.PSL_NORMAL_SECURITY);


	create_ct(server)


		

	server.logoff() #log off
	prlsdkapi.deinit_sdk() # deinitialize the library.



if __name__ == "__main__":
	main()
