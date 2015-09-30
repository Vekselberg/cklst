#!/usr/bin/env python

try:
	import prlsdkapi
except:
	print 'Failed to import Parallels SDK\nUnable to continue.\n'
	exit(1)

import logging, time, commands, hashlib, re
from config import *
from uuid import uuid4

host_slicer=lambda x: re.split('[:@]',x)
spacer = lambda x: x + '\n'

sshckbypass='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no '
consts = prlsdkapi.prlsdk.consts
ssh_s_node=sshckbypass+source_node
ssh_d_node=sshckbypass+dest_node
PCS_ver=[]
CT={}
CT_MD5_list={}


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
	PCS_ver.append(product_version)
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
	net.set_auto_apply(True)
	net.set_bound_adapter_index(net_adapter.get_sys_index())
	net.set_bound_adapter_name(net_adapter.get_name())
	try:
		vm.commit().wait()
	except prlsdkapi.PrlSDKError, e:
		print "Error: %s" % e
		return 


def create_bigfile(): 
	
	for ctname in CT_MD5_list.keys():
		dd=' \'prlctl exec %s \'dd if=/dev/urandom of=/testfile bs=1M count=52\'\'' %ctname
		commands.getoutput(sshckbypass+'-i dest '+host_slicer(source_node)[0]+'@'+host_slicer(source_node)[2]+dd)
		md5_checks(ctname)

def md5_checks(ct):
	md5=' \'prlctl exec %s \'md5sum /testfile\'\'' %ct
	sum=commands.getoutput(sshckbypass+'-i dest '+host_slicer(source_node)[0]+'@'+host_slicer(source_node)[2]+md5).replace('\n'," ")
	if CT_MD5_list[ct]=="":
		CT_MD5_list[ct]=re.findall('\w[0-9a-z]{31}',sum)[0]
	else:
		if CT_MD5_list[ct]==re.findall('\w[0-9a-z]{31}',sum)[0]:
			print 'MD5 check for CT: %s PASSED.' %ct
		else:
			print 'MD5 check for CT: %s FAILED.' %ct


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
	CT_MD5_list[name]=""
	CT[name]=ct
	ct.start().wait()
	print ct.get_uuid()

def clone(ct):
	ct2 = ct.clone('121', '').wait().get_param()
	print('Clone name = %s' % ct2.get_name())


def search_vm(server, vm_to_find):
	try:
		result = server.get_vm_list().wait()
	except prlsdkapi.PrlSDKError, e:
		print "Error: %s" % e
		return            
	for i in range(result.get_params_count()):
		vm = result.get_param_by_index(i)
		vm_name = vm.get_name()
		print vm_name
		if vm_name.startswith(vm_to_find):
			return vm
	print 'Virtual server "' + vm_to_find + '" not found.'





def switcher(vm, action):
	if action=="stop":
		try:
			vm.stop(True).wait()
		except prlsdkapi.PrlSDKError, e:
                        logging.debug("Error: %s" % e)
			raise halt
	if action=="start":
		try:
			vm.start().wait()
		except prlsdkapi.PrlSDKError, e:
                        logging.debug("Error: %s" % e)
			raise halt
	if action=="pause": #unimplemented yet
		try:
			vm.pause(True).wait()
		except prlsdkapi.PrlSDKError, e:
                        logging.debug("Error: %s" % e)
			raise halt
	if action=="resume":
		try:
			vm.resume().wait()
		except prlsdkapi.PrlSDKError, e:
                        logging.debug("Error: %s" % e)
			raise halt
	if action=="restart":
		try:
			vm.restart().wait()
		except prlsdkapi.PrlSDKError, e:
			logging.debug("Error: %s" % e)
			raise halt

	if action=="reset": #unimplemented yet
		try:
			vm.reset().wait()
		except prlsdkapi.PrlSDKError, e:
			logging.debug("Error: %s" % e)
			raise halt
	if action=="suspend":
                try:
                        vm.suspend().wait()
                except prlsdkapi.PrlSDKError, e:
			logging.debug("Error: %s" % e)
			raise halt


def scope1(ct):
#stop,start,suspend,resume,restart
	try:
		switcher(ct,'stop')
		logging.info('CT %s STOPPED' %ct)
		print '* STOP passed'
	except:
		logging.error('CT %s STOP FAILED' %ct)
		print '* STOP failed'
	#raw_input()
	try:
		switcher(ct,'start')
		logging.info('CT %s STARTED' %ct)
		print '* START passed'
	except:
		logging.error('CT %s START FAILED' %ct)
		print '* START failed'
	try:
		switcher(ct,'suspend')
		logging.info('CT %s SUSPENDED' %ct)
		print '* SUSPEND passed'
	except:
		logging.error('CT %s SUSPEND FAILED' %ct)
		print '* SUSPEND failed'
	try:
                switcher(ct,'resume')
                logging.info('CT %s RESUMED' %ct)
		print '* RESUME passed'
        except:
                logging.error('CT %s RESUME FAILED' %ct)
		print '* RESUME failed'
	try:
                switcher(ct,'restart')
                logging.info('CT %s RESTARTED' %ct)
		print '* RESTART passed'
        except:
                logging.error('CT %s RESTART FAILED' %ct)
		print '* RESTART failed'

def cleanup():
	print ''
	print 'Cleaning up...'
	for i in CT.values():
		switcher(i, 'stop')
		i.delete()


def main():
	logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename="checklist.log",filemode='w', level=logging.DEBUG)
	print '1'
	prlsdkapi.init_server_sdk() # Initialize the library.
	server = prlsdkapi.Server() # Create a Server object
 	login_server(server, host_slicer(source_node)[2], host_slicer(source_node)[0], host_slicer(source_node)[1], consts.PSL_NORMAL_SECURITY);

	for r in xrange(1,6):
		create_ct(server)
	print 'Creating content...'
	create_bigfile()
#	print CT_MD5_list
	logging.debug('[VE] %s' %CT_MD5_list.items())
	
	
	#create snapshot CT#2
	try:
		CT[CT.keys()[1]].create_snapshot('testfile')
		print "Snapshot created"
		
	except:
		print "Snapshot creation failure"

	print ''
	print 'First scope started'
	scope1(CT[CT.keys()[0]])
	print ''
#	switcher(CT[CT.keys()[0]],'stop')
#	CT[CT.keys()[0]].delete()
	clone(CT[CT.keys()[1]])
		

#	print CT[CT.keys()[1]].get_uuid()
#	job=CT[CT.keys()[1]].get_snapshots_tree()
#	job.wait()
#	result=job.get_result()
#	print CT.keys()[1] 
#	print result.get_param_as_string()

	#cleanup()



	server.logoff() #log off
	prlsdkapi.deinit_sdk() # deinitialize the library.


if __name__ == "__main__":
	main()
