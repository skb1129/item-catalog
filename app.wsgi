#!/usr/bin/python
import os, sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/moviecafe/")

from moviecafe.app import app as application
application.secret_key = os.urandom(12)
