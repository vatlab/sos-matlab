#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

from sos_notebook.test_utils import NotebookTest
import random
import shutil
import pytest

@pytest.mark.skipif(not shutil.which('matlab'), reason='MATLAB is not available')
class TestMATLABDataExchange(NotebookTest):

    def _var_name(self):
        if not hasattr(self, '_var_idx'):
            self._var_idx = 0
        self._var_idx += 1
        return f'var{self._var_idx}'

    def get_from_SoS(self, notebook, sos_expr):
        var_name = self._var_name()
        notebook.call(f'{var_name} = {sos_expr}', kernel='SoS')
        return notebook.check_output(
            f'''\
            %get {var_name}
            disp({var_name})
            ''',
            kernel='MATLAB')

    def put_to_SoS(self, notebook, py2_expr):
        var_name = self._var_name()
        notebook.call(
            f'''\
            %put {var_name}
            {var_name} = {py2_expr}
            ''',
            kernel='MATLAB')
        return notebook.check_output(f'print(repr({var_name}))', kernel='SoS')

    def test_get_none(self, notebook):
        assert 'NaN' == self.get_from_SoS(notebook, 'None')

    def test_put_NaN(self, notebook):
        assert 'None' == self.put_to_SoS(notebook, 'NaN')

    def test_get_int(self, notebook):
        assert 123 == int(self.get_from_SoS(notebook, '123'))
        assert '1.2346e+12' == self.get_from_SoS(notebook, '1234567891234')

    def test_put_int(self, notebook):
        assert 123 == int(self.put_to_SoS(notebook, '123'))
        assert 1234567891234 == int(self.put_to_SoS(notebook, '1234567891234'))
        # rounding error occurs
        assert 123456789123456784 == int(
            self.put_to_SoS(notebook, '123456789123456789'))

    def test_get_double(self, notebook):
        val = str(random.random())
        notebook.call('format long', kernel='MATLAB')
        assert abs(float(val) - float(self.get_from_SoS(notebook, val))) < 1e-10

    def test_put_double(self, notebook):
        val = str(random.random())
        notebook.call('format long', kernel='MATLAB')
        assert abs(float(val) - float(self.put_to_SoS(notebook, val))) < 1e-10

    def test_get_logic(self, notebook):
        assert '1' == self.get_from_SoS(notebook, 'True')
        assert '0' == self.get_from_SoS(notebook, 'False')

    def test_put_logic(self, notebook):
        assert 'True' == self.put_to_SoS(notebook, 'true')
        assert 'False' == self.put_to_SoS(notebook, 'false')

    def test_get_num_array(self, notebook):
        assert '1' == self.get_from_SoS(notebook, '[1]')
        assert '1\n2' == self.get_from_SoS(notebook, '[1, 2]').replace(' ', '')
        #
        notebook.call('format short', kernel='MATLAB')
        assert '1.2300' == self.get_from_SoS(notebook, '[1.23]')
        assert '1.4000\n2.0000' == self.get_from_SoS(notebook,
                                                     '[1.4, 2]').replace(
                                                         ' ', '')

    def test_get_numpy_array(self, notebook):
        notebook.call('import numpy as np', kernel='SoS')
        assert ['1', '2', '3'] == self.get_from_SoS(notebook, 'np.array([1, 2, 3])').split()
        notebook.call('format short', kernel='MATLAB')
        assert ['11.0000', '2.1000', '32.0000'] == self.get_from_SoS(
            notebook, 'np.array([11, 2.1, 32])').split()

    def test_put_num_array(self, notebook):
        assert '1' == self.put_to_SoS(notebook, '[1]')
        assert 'array([1, 2])' == self.put_to_SoS(notebook, '[1, 2]')
        #
        assert '1.23' == self.put_to_SoS(notebook, '[1.23]')
        assert 'array([1.4, 2. ])' == self.put_to_SoS(notebook, '[1.4, 2]')

    def test_get_logic_array(self, notebook):
        assert '1' == self.get_from_SoS(notebook, '[True]')
        assert '1\n0\n1' == self.get_from_SoS(notebook,
                                              '[True, False, True]').replace(
                                                  ' ', '')

    def test_put_logic_array(self, notebook):
        # Note that single element numeric array is treated as single value
        assert 'True' == self.put_to_SoS(notebook, '[true]')
        assert '[True, False, True]' == self.put_to_SoS(notebook,
                                                        '[true, false, true]')

    def test_get_str(self, notebook):
        assert "ab c d" == self.get_from_SoS(notebook, "'ab c d'")
        assert "ab\\td" == self.get_from_SoS(notebook, r"'ab\td'")

    def test_put_str(self, notebook):
        assert "'ab c d'" == self.put_to_SoS(notebook, "'ab c d'")
        assert r"'ab\\td'" == self.put_to_SoS(notebook, r"'ab\td'")

    def test_get_str_array(self, notebook):
        output = self.get_from_SoS(notebook, "['a1', 'a2', 'a3']")
        assert 'a1' in output and 'a2' in output and 'a3' in output

    def test_put_str_array(self, notebook):
        # NOTE: MATLAB only accepts strings with the same size
        assert "['a1a1', 'a2a2', 'a3cv']" == self.put_to_SoS(
            notebook, "['a1a1'; 'a2a2'; 'a3cv']")

    def test_get_mixed_list(self, notebook):
        output = self.get_from_SoS(notebook, '[2.4, True, "asd"]')
        assert '2.4' in output and '1' in output and 'asd' in output

    def test_get_dict(self, notebook):
        output = self.get_from_SoS(notebook, "dict(a=1, b='2')")
        assert 'a: 1' in output and "b: '2'" in output

    def test_get_set(self, notebook):
        output = self.get_from_SoS(notebook, "{1.5, 'abc'}")
        assert '1.5' in output or abc in output

    def test_get_complex(self, notebook):
        assert "1.0000 + 2.2000i" == self.get_from_SoS(notebook,
                                                       "complex(1, 2.2)")

    def test_put_complex(self, notebook):
        assert "(2+3j)" == self.put_to_SoS(notebook, "2+3i")

    def test_get_recursive(self, notebook):
        output = self.get_from_SoS(notebook,
                                   "{'a': 1, 'b': {'c': 3, 'd': 'whatever'}}")
        assert 'a: 1' in output and 'b: [1x1 struct]' in output

    def test_get_matrix(self, notebook):
        notebook.call('import numpy as np', kernel='SoS')
        output = self.get_from_SoS(notebook, 'np.matrix([[11,22],[33,44]])')
        assert all(x in output for x in ('11', '22', '33', '44'))

    def test_put_matrix(self, notebook):
        output = self.put_to_SoS(notebook, '[1:3; 2:4]')
        assert 'matrix' in output and '[1, 2, 3]' in output and '[2, 3, 4]' in output

    def test_get_ndarray(self, notebook):
        notebook.call(
            '''\
            %put var_3d --to MATLAB
            from numpy import zeros
            var_3d = zeros([2, 3, 4])
        ''',
            kernel='SoS')
        assert ['2', '3', '4'] == notebook.check_output(
            'disp(size(var_3d))', kernel='MATLAB').split()

    def test_put_ndarray(self, notebook):
        notebook.call(
            '''\
            %put MATLAB_var_3d
            MATLAB_var_3d = zeros([2, 3, 4])
        ''',
            kernel='MATLAB')
        assert '(2, 3, 4)' == notebook.check_output(
            'MATLAB_var_3d.shape', kernel='SoS')

    def test_get_dataframe(self, notebook):
        notebook.call(
            '''\
            %put df --to MATLAB
            import pandas as pd
            import numpy as np
            arr = np.random.randn(100)
            df = pd.DataFrame({'column_{0}'.format(i): arr for i in range(10)})
            ''',
            kernel='SoS')
        output = notebook.check_output('df', kernel='MATLAB')
        assert '100x10 table' in output
        #
        #  non-numeric dataframe
        notebook.call(
            '''\
            %put df --to MATLAB
            import pandas as pd

            df = pd.DataFrame({'name': ['Leonardo', 'Donatello', 'Michelangelo', 'Raphael'],
                   'mask': ['blue', 'purple', 'orange', 'red'],
                   'weapon': ['ninjatos', 'bo', 'nunchaku', 'sai']})
            ''',
            kernel='SoS')
        output = notebook.check_output('df', kernel='MATLAB')
        assert '4x3 table' in output and 'Michelangelo' in output
