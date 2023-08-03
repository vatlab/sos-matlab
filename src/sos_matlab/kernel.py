#!/usr/bin/env python3
#
# Copyright (c) Bo Peng and the University of Texas MD Anderson Cancer Center
# Distributed under the terms of the 3-clause BSD License.

import csv
import os
import tempfile
from collections.abc import Sequence

import numpy as np
import pandas as pd
import scipy.io as sio
from sos.utils import env


def homogeneous_type(seq):
    iseq = iter(seq)
    first_type = type(next(iseq))
    if first_type in (int, float):
        return True if all(isinstance(x, (int, float)) for x in iseq) else False
    return True if all(isinstance(x, first_type) for x in iseq) else False


Matlab_init_statements = rf'''
path(path, {os.path.split(__file__)[0]!r})
'''


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
        if isinstance(obj, (int, float, str, complex)):
            return repr(obj)
        if isinstance(obj, Sequence):
            if len(obj) == 0:
                return '[]'

            # if the data is of homogeneous type, let us use []

            if homogeneous_type(obj):
                return '[' + ';'.join(self._Matlab_repr(x) for x in obj) + ']'
            return '{' + ';'.join(self._Matlab_repr(x) for x in obj) + '}'
        if obj is None:
            return 'NaN'
        if isinstance(obj, dict):
            dic = tempfile.tempdir
            sio.savemat(os.path.join(dic, 'dict2mtlb.mat'), {'obj': obj})
            return 'getfield(load(fullfile(' + '\'' + dic + '\'' + ',' \
                + '\'dict2mtlb.mat\')), \'obj\')'

        if isinstance(obj, set):
            return '{' + ','.join(self._Matlab_repr(x) for x in obj) + '}'
        if isinstance(obj, (
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

        if isinstance(obj, np.matrixlib.defmatrix.matrix):
            dic = tempfile.tempdir
            sio.savemat(os.path.join(dic, 'mat2mtlb.mat'), {'obj': obj})
            return 'cell2mat(struct2cell(load(fullfile(' + '\'' + dic + '\'' + ',' \
                + '\'mat2mtlb.mat\'))))'
        if isinstance(obj, np.ndarray):
            dic = tempfile.tempdir
            sio.savemat(os.path.join(dic, 'ary2mtlb.mat'), {'obj': obj})
            return 'sos_load_obj(fullfile(' + '\'' + dic + '\'' + ',' \
                + '\'ary2mtlb.mat\'))'
        if isinstance(obj, pd.DataFrame):
            if self.kernel_name == 'octave':
                dic = tempfile.tempdir
                obj.to_csv(os.path.join(dic, 'df2oct.csv'), index=False, quoting=csv.QUOTE_NONNUMERIC, quotechar="'")
                return 'dataframe(' + '\'' + dic + '/' + 'df2oct.csv\')'
            dic = tempfile.tempdir
            obj.to_csv(os.path.join(dic, 'df2mtlb.csv'), index=False, quoting=csv.QUOTE_NONNUMERIC, quotechar="'")
            return 'readtable(' + '\'' + dic + '/' + 'df2mtlb.csv\')'

    async def get_vars(self, names, as_var=None):
        for name in names:
            # add 'm' to any variable beginning with '_'
            if as_var is not None:
                newname = as_var
            elif name.startswith('_'):
                self.sos_kernel.warn(f'Variable {name} is passed from SoS to kernel {self.kernel_name} as {"m" + name}')
                newname = 'm' + name
            else:
                newname = name
            matlab_repr = self._Matlab_repr(env.sos_dict[name])
            env.log_to_file('KERNEL', f'Executing \n{matlab_repr}')
            await self.sos_kernel.run_cell(
                f'{newname} = {matlab_repr}',
                True,
                False,
                on_error=f'Failed to get variable {name} of type {env.sos_dict[name].__class__.__name__} to Matlab')

    def put_vars(self, items, to_kernel=None, as_var=None):
        if not items:
            return {}

        result = {}
        for item in items:
            py_repr = f'display(sos_py_repr({item}))'
            #9 MATLAB can use multiple messages for standard output,
            # so we need to concatenate these outputs.
            expr = ''
            for _, msg in self.sos_kernel.get_response(py_repr, ('stream',), name=('stdout',)):
                expr += msg['text']

            cwd = os.getcwd()
            try:
                if 'loadmat' in expr:
                    # imported to be used by eval
                    from scipy.io import loadmat
                # evaluate as raw string to correctly handle \\ etc
                result[as_var if as_var else item] = eval(expr)
            except Exception as e:
                self.sos_kernel.warn(f'Failed to evaluate {expr!r}: {e}')
            finally:
                os.chdir(cwd)
        return result

    def sessioninfo(self):
        return self.sos_kernel.get_response(r'ver', ('stream',), name=('stdout',))[0][1]['text']
