#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import pandas as pd
import csv
import numpy as np
import scipy.io as sio
import os
from collections import Sequence
import tempfile
from sos.utils import short_repr, env
from IPython.core.error import UsageError

def homogeneous_type(seq):
    iseq = iter(seq)
    first_type = type(next(iseq))
    if first_type in (int, float):
        return True if all(isinstance(x, (int, float)) for x in iseq) else False
    else:
        return True if all(isinstance(x, first_type) for x in iseq) else False

Matlab_init_statements = r'''
path(path, {!r})
'''.format(os.path.split(__file__)[0])

class sos_MATLAB:
    supported_kernels = {'MATLAB': ['imatlab', 'matlab'], 'Octave': ['octave']}
    background_color = {'MATLAB': '#8ee7f1', 'Octave': '#dff8fb'}
    options = {}
    cd_command = 'cd {dir}'

    def __init__(self, sos_kernel, kernel_name='matlab'):
        self.sos_kernel = sos_kernel
        self.kernel_name = kernel_name
        self.init_statements = Matlab_init_statements
        if self.kernel_name == 'octave':
            self.init_statements += 'pkg load dataframe\n'

    def _Matlab_repr(self, obj):
        #  Converting a Python object to a Matlab expression that will be executed
        #  by the Matlab kernel.
        if isinstance(obj, bool):
            return 'true' if obj else 'false'
        elif isinstance(obj, (int, float, str, complex)):
            return repr(obj)
        elif isinstance(obj, Sequence):
            if len(obj) == 0:
                return '[]'

            # if the data is of homogeneous type, let us use []

            if homogeneous_type(obj):
                return '[' + ';'.join(self._Matlab_repr(x) for x in obj) + ']'
            else:
                return '{' + ';'.join(self._Matlab_repr(x) for x in obj) + '}'
        elif obj is None:
            return 'NaN'
        elif isinstance(obj, dict):
            dic = tempfile.tempdir
            os.chdir(dic)
            sio.savemat('dict2mtlb.mat', {'obj': obj})
            return 'getfield(load(fullfile(' + '\'' + dic + '\'' + ',' \
                + '\'dict2mtlb.mat\')), \'obj\')'

        elif isinstance(obj, set):
            return '{' + ','.join(self._Matlab_repr(x) for x in obj) + '}'
        elif isinstance(obj, (
                              np.intc,
                              np.intp,
                              np.int8,
                              np.int16,
                              np.int32,
                              np.int64,
                              np.uint8,
                              np.uint16,
                              np.uint32,
                              np.uint64,
                              np.float16,
                              np.float32,
                              np.float64,
                              )):
            return repr(obj)

        elif isinstance(obj, np.matrixlib.defmatrix.matrix):
            dic = tempfile.tempdir
            os.chdir(dic)
            sio.savemat('mat2mtlb.mat', {'obj': obj})
            return 'cell2mat(struct2cell(load(fullfile(' + '\'' + dic + '\'' + ',' \
                + '\'mat2mtlb.mat\'))))'
        elif isinstance(obj, np.ndarray):
            dic = tempfile.tempdir
            os.chdir(dic)
            sio.savemat('ary2mtlb.mat', {'obj': obj})
            return 'sos_load_obj(fullfile(' + '\'' + dic + '\'' + ',' \
                + '\'ary2mtlb.mat\'))'
        elif isinstance(obj, pd.DataFrame):
            if self.kernel_name == 'octave':
                dic = tempfile.tempdir
                os.chdir(dic)
                obj.to_csv('df2oct.csv', index=False, quoting=csv.QUOTE_NONNUMERIC, quotechar="'")
                return 'dataframe(' + '\'' + dic + '/' + 'df2oct.csv\')'
            else:
                dic = tempfile.tempdir
                os.chdir(dic)
                obj.to_csv('df2mtlb.csv', index=False, quoting=csv.QUOTE_NONNUMERIC, quotechar="'")
                return 'readtable(' + '\'' + dic + '/' + 'df2mtlb.csv\')'

    def get_vars(self, names):
        for name in names:
            # add 'm' to any variable beginning with '_'
            if name.startswith('_'):
                self.sos_kernel.warn('Variable {} is passed from SoS to kernel {} as {}'.format(name, self.kernel_name, 'm' + name))
                newname = 'm' + name
            else:
                newname = name
            matlab_repr = self._Matlab_repr(env.sos_dict[name])
            if self.sos_kernel._debug_mode:
                self.sos_kernel.warn(matlab_repr)
            self.sos_kernel.run_cell('{} = {}'.format(newname, matlab_repr), True, False,
                    on_error='Failed to get variable {} of type {} to Matlab'.format(name, env.sos_dict[name].__class__.__name__))

    def put_vars(self, items, to_kernel=None):
        # first let us get all variables with names starting with sos
        response = self.sos_kernel.get_response("who('sos*')", ('stream',), name=('stdout',))
        for line in response:
            # The prompt are filtered bu the sos prefix
            items.extend([x for x in line[1]['text'].strip().split() if x.startswith('sos')])

        if not items:
            return {}

        result = {}
        for item in items:
            py_repr = 'display(sos_py_repr({}))'.format(item)
            response = self.sos_kernel.get_response(py_repr, ('stream',), name=('stdout',))[0][1]
            expr = response['text']

            try:
                if 'loadmat' in expr:
                    # imported to be used by eval
                    from scipy.io import loadmat
                # evaluate as raw string to correctly handle \\ etc
                result[item] = eval(expr)
            except Exception as e:
                self.sos_kernel.warn('Failed to evaluate {!r}: {}'.format(expr, e))
        return result

    def sessioninfo(self):
        return self.sos_kernel.get_response(r'ver', ('stream',), name=('stdout',))[0][1]['text']
