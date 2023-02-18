import argparse
import re
import sys

import nbformat
from nbformat.v4 import new_code_cell, new_notebook
from sos.utils import env


class OctaveToNotebookConverter(object):

    def get_parser(self):
        parser = argparse.ArgumentParser(
            'sos convert FILE.m FILE.ipynb (or --to ipynb)',
            description='''Convert an Octave or Matlab .m script to Jupyter notebook (.ipynb)
                so that it can be opened by Jupyter notebook.''')
        parser.add_argument(
            '--kernel',
            choices={'matlab', 'octave'},
            default='octave',
            help='Kernel to use, octave or matlab, default to octave.')
        parser.add_argument(
            '--use-sos',
            action='store_true',
            help='''generate a sos notebook (with octave or matlab as a subkernel),
                or a Notebook using Octave or Matlab kernel directly.''')
        return parser

    def convert(self, script_file, notebook_file, args=None, unknown_args=None):
        '''
        Convert a .m script to a Jupyter notebook with a single cell.
        '''
        if unknown_args:
            raise ValueError(f'Unrecognized parameter {unknown_args}')
        with open(script_file, 'r') as src:
            metainfo = {}
            if args.use_sos:
                metainfo = {'kernel': 'SoS'}

            cells = [
                new_code_cell(
                    source=line.rstrip(),
                    execution_count=count + 1,
                    metadata=metainfo)
                for count, line in enumerate(re.split(r'\n\s*\n', src.read()))
            ]

        #
        metadata = {}
        if args.use_sos:
            if args.kernel == 'octave':
                kernelspec = ["Octave", "octave", "Octave", "#dff8fb", ""]
            else:
                kernelspec = ["MATLAB", "matlab", "MATLAB", "#dff8fb", ""]
            metadata = {
                'kernelspec': {
                    "display_name": "SoS",
                    "language": "sos",
                    "name": "sos"
                },
                "language_info": {
                    'codemirror_mode': 'sos',
                    "file_extension": ".sos",
                    "mimetype": "text/x-sos",
                    "name": "sos",
                    "pygments_lexer": "python",
                    'nbconvert_exporter': 'sos_notebook.converter.SoS_Exporter',
                },
                'sos': {
                    'kernels': [['SoS', 'sos', '', ''], kernelspec]
                }
            }
        elif args.kernel == 'octave':
            metadata = {
                "kernelspec": {
                    "display_name": "Octave",
                    "language": "octave",
                    "name": "octave"
                },
                "language_info": {
                    "file_extension": ".m",
                    "help_links": [{
                        "text":
                            "GNU Octave",
                        "url":
                            "https://www.gnu.org/software/octave/support.html"
                    }, {
                        "text": "Octave Kernel",
                        "url": "https://github.com/Calysto/octave_kernel"
                    }, {
                        "text":
                            "MetaKernel Magics",
                        "url":
                            "https://metakernel.readthedocs.io/en/latest/source/README.html"
                    }],
                    "mimetype": "text/x-octave",
                    "name": "octave",
                    "version": "6.2.0"
                }
            }
        else:
            metadata = {
                "kernelspec": {
                    "display_name": "Matlab",
                    "language": "matlab",
                    "name": "matlab"
                },
                "language_info": {
                    "codemirror_mode": "octave",
                    "file_extension": ".m",
                    "help_links": [{
                        "text":
                            "MetaKernel Magics",
                        "url":
                            "https://github.com/calysto/metakernel/blob/master/metakernel/magics/README.md"
                    }],
                    "mimetype": "text/x-matlab",
                    "name": "matlab",
                    "version": "0.14.3"
                }
            }

        nb = new_notebook(cells=cells, metadata=metadata)
        if not notebook_file:
            nbformat.write(nb, sys.stdout, 4)
        else:
            with open(notebook_file, 'w') as notebook:
                nbformat.write(nb, notebook, 4)
            env.logger.info(f'Jupyter notebook saved to {notebook_file}')
