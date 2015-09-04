#!/usr/bin/env python
#try:
#	import prlsdkapi
#except:
#	print 'Failed to import Parallels SDK'


import logging, time, commands,hashlib
from config import *
from uuid import uuid4

spacer = lambda x: x + '\n'
def output_w(result):
	with open('results.log', 'a') as file:
		file.write(spacer(result))








def main():
	output_w('t')
	output_w('q')
main()
