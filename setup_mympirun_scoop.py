#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Copyright 2009-2012 Ghent University
# Copyright 2009-2012 Stijn De Weirdt
# Copyright 2012 Andy Georges
#
# This file is part of VSC-tools,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/VSC-tools
#
# VSC-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# VSC-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VSC-tools. If not, see <http://www.gnu.org/licenses/>.
#
"""
Setup for the SCOOP functionality of mympirun
"""

from shared_setup import sdw
from shared_setup import action_target
from setup_mympirun import mympirun_vsc_install_scripts



PACKAGE = {
    'name': 'vsc-mympirun-scoop',
    'install_requires': ['vsc-processcontrol >= 0.90',
                         'vsc-mympirun >= 3.0.7',
                         'vsc-base >= 0.96',
                         'scoop >= 0.5.3',
                         ],
    'version': '3.0.10',
    'author': [sdw],
    'maintainer': [sdw],
    'packages': ['vsc.mympirun.scoop', 'vsc.mympirun.scoop.worker'],
    'namespace_packages': ['vsc', 'vsc.mympirun'],
    'py_modules': ['vsc.__init__', 'vsc.mympirun.__init__'],
    # 'scripts':['bin/mympirun.py'], ## is installed with vsc-mympirun, including myscoop
    'cmdclass': {
        "install_scripts": mympirun_vsc_install_scripts,  # this is required for easy_install for the egg_install_scripts
    },

}

if __name__ == '__main__':
    action_target(PACKAGE, extra_sdist=['setup_mympirun.py'])
