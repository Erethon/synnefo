# Copyright 2012, 2013 GRNET S.A. All rights reserved.
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
#   1. Redistributions of source code must retain the above
#      copyright notice, this list of conditions and the following
#      disclaimer.
#
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY GRNET S.A. ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL GRNET S.A OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and
# documentation are those of the authors and should not be
# interpreted as representing official policies, either expressed
# or implied, of GRNET S.A.

### IMPORTS ###
import sys
import os
import subprocess
import time
from errno import ECONNREFUSED
from os.path import dirname

path = os.path.dirname(os.path.realpath(__file__))
os.environ['SYNNEFO_SETTINGS_DIR'] = path + '/settings'
os.environ['DJANGO_SETTINGS_MODULE'] = 'synnefo.settings'

# The following import is copied from snf-tools/syneffo_tools/burnin.py
# Thank you John Giannelos <johngian@grnet.gr>
# Use backported unittest functionality if Python < 2.7
try:
    import unittest2 as unittest
except ImportError:
    if sys.version_info < (2, 7):
        raise Exception("The unittest2 package is required for Python < 2.7")
    import unittest

from astakos.quotaholder.callpoint import QuotaholderDjangoDBCallpoint

import random

def printf(fmt, *args):
    print(fmt.format(*args))


### DEFS ###
def new_quota_holder_client():
    """
    Create a new quota holder api client
    """
    return QuotaholderDjangoDBCallpoint()

def run_test_case(test_case):
    """
    Runs the test_case and returns the result
    """
    # Again from snf-tools/synnefo_tools/burnin.py
    # Thank you John Giannelos <johngian@grnet.gr>
    printf("Running {0}", test_case)
    import sys
    suite = unittest.TestLoader().loadTestsFromTestCase(test_case)
    runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=2,
                                     failfast=True, buffer=False)
    return runner.run(suite)

def run_test_cases(test_cases):
    for test_case in test_cases:
        run_test_case(test_case)

def rand_string():
   alphabet = 'abcdefghijklmnopqrstuvwxyz'
   min = 5
   max = 15
   string=''
   for x in random.sample(alphabet,random.randint(min,max)):
    string += x
   return string

HERE = dirname(__file__)

### CLASSES ###
class QHTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        subprocess.call([HERE+'/qh_init'])
        self.qh = new_quota_holder_client()

    def setUp(self):
        print

    @classmethod
    def tearDownClass(self):
        pass
