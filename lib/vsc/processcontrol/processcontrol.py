#
# Copyright 2013-2013 Ghent University
# Copyright 2013-2013 Stijn De Weirdt
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
Some common classes and functions
"""
import os

try:
    from vsc.fancylogger import getLogger
except:
    from logging import getLogger

class DummyFunction(object):
    def __getattr__(self, name):
        def dummy(*args, **kwargs):
            pass
        return dummy

class InitLog(object):
    """Base class to set logger
        - set logger in __init__ to log attr
    """
    def __init__(self, *args, **kwargs):
        """
            - disable_log : boolean use dummy logger
        """
        disable_log = kwargs.pop('disable_log', False)
        if disable_log:
            log = DummyFunction()
        else:
            log = getLogger(self.__class__.__name__)
        self.log = log

class ProcessControlBase(InitLog):
    """Base class for all process control classes
        - set pid attribute
    """
    def __init__(self, *args, **kwargs):
        """
            - disable_log : boolean use dummy logger
            - pid : int process id
        """
        pid = kwargs.pop('pid', None)
        super(ProcessControlBase, self).__init__(*args, **kwargs)

        if pid is None:
            pid = os.getpid()
        else:
            pid = int(pid)
        self.pid = pid
