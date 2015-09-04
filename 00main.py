#!/usr/bin/env python
try:
	import prlsdkapi
except:
	print 'Failed to import Parallels SDK'
	

import logging, time, commands
from config import *
from uuid import uuid4
