#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import os
import unittest
import shutil
from ipykernel.tests.utils import assemble_output, execute, wait_for_idle
from sos_notebook.test_utils import sos_kernel, get_result, clear_channels

class TestOctaveKernel(unittest.TestCase):
    #
    # Beacuse these tests would be called from sos/test, we
    # should switch to this directory so that some location
    # dependent tests could run successfully
    #
    def setUp(self):
        self.olddir = os.getcwd()
        if os.path.dirname(__file__):
            os.chdir(os.path.dirname(__file__))

    def tearDown(self):
        os.chdir(self.olddir)

    @unittest.skipIf(not shutil.which('octave'), 'Octave not installed')
    def testGetInt(self):
        '''Test sending integers to SoS'''
        with sos_kernel() as kc:
            iopub = kc.iopub_channel
            execute(kc=kc, code='''
int1 = 123
int2 = 12345678901234567
''')
            clear_channels(iopub)
            execute(kc=kc, code="""
%use Octave
%get int1 int2
""")
            wait_for_idle(kc)
            execute(kc=kc, code="int1")
            wait_for_idle(kc)
            execute(kc=kc, code="int2")
            wait_for_idle(kc)





if __name__ == '__main__':
    unittest.main()

