#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import os
import tempfile
import pytest
from sos_notebook.test_utils import NotebookTest

import shutil
import pytest


@pytest.mark.skipif(
    not shutil.which('matlab'), reason='MATLAB is not available')
class TestMATLABInterface(NotebookTest):

    #
    # Python 2
    #
    def test_prompt_color(self, notebook):
        '''test color of input and output prompt'''
        idx = notebook.call(
            '''\
            disp('this is MATLAB')
            ''',
            kernel="MATLAB")
        assert [142, 231, 241] == notebook.get_input_backgroundColor(idx)
        assert [142, 231, 241] == notebook.get_output_backgroundColor(idx)

    def test_cd(self, notebook):
        '''Support for change of directory with magic %cd'''
        output1 = notebook.check_output(
            '''\
            disp(pwd)
            ''', kernel="MATLAB")
        notebook.call('%cd ..', kernel="SoS")
        output2 = notebook.check_output(
            '''\
            disp(pwd)
            ''', kernel="MATLAB")
        assert len(output1) > len(output2)
        assert output1.startswith(output2)
        #
        # cd to a specific directory
        tmpdir = os.path.join(tempfile.gettempdir(), 'somedir')
        os.makedirs(tmpdir, exist_ok=True)
        notebook.call(f'%cd {tmpdir}', kernel="SoS")
        output = notebook.check_output(
            '''\
            disp(pwd)
            ''', kernel="MATLAB")
        assert os.path.realpath(tmpdir) == os.path.realpath(output)

    # def test_preview(self, notebook):
    #     '''Test support for %preview'''
    #     output = notebook.check_output(
    #         '''\
    #         %preview -n var
    #         var = list(range(100))
    #         ''',
    #         kernel="MATLAB")
    #     # in a normal var output, 100 would be printed. The preview version would show
    #     # type and some of the items in the format of
    #     #   int [1:1000] 1 2 3 4 5 6 7 8 9 10 ...
    #     assert 'list' in output and '100' in output and '1' in output and '99' not in output

    #     #
    #     # return 'Unknown variable' for unknown variable
    #     assert 'Unknown variable' in notebook.check_output(
    #         '%preview -n unknown_var', kernel="MATLAB")
    #     #
    #     # return 'Unknown variable for expression
    #     assert 'Unknown variable' in notebook.check_output(
    #         '%preview -n var[1]', kernel="MATLAB")

    def test_sessioninfo(self, notebook):
        '''test support for %sessioninfo'''
        notebook.call("disp('this is MATLAB')", kernel="MATLAB")
        assert 'MATLAB' in notebook.check_output('%sessioninfo', kernel="SoS")
