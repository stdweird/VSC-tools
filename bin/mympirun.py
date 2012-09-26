#!/usr/bin/env python
##
# Copyright 2009-2012 Stijn De Weirdt
#
# This file is part of VSC-tools,
# originally created by the HPC team of the University of Ghent (http://ugent.be/hpc).
#
#
# http://github.com/hpcugent/VSC-tools
#
# VSC-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# EasyBuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VSC-tools. If not, see <http://www.gnu.org/licenses/>.
##

"""
A mpirun wrapper

Stijn De Weirdt HPC UGent / VSC
v1 bash 10/08/2009
v2 python rewrite 19/03/2010
v3 refactored python 28/08/2012

Expert mode:
    export MYMPIRUN_MAIN_EXCEPTION=1 to show all exceptions

TODO:
    force the prefix to MYMPIRUN ?
    intel tuning code
"""

from vsc.mympirun.option import MympirunOption
from vsc.mympirun.mpi.mpi import whatMPI
from vsc.mympirun.rm.sched import whatSched
from vsc.fancylogger import getLogger, setLogLevelInfo

import sys, os

_logger = getLogger()

class ExitException(Exception):
    """Raise and main sees this as regular exit"""
    pass

def getInstance():
    """Make an instance of the relevant MPI class. Also set the RM instance"""
    scriptname, mpi, found_mpi = whatMPI(sys.argv[0])

    ismpirun = scriptname == 'mpirun'

    mo = MympirunOption(ismpirun=ismpirun)

    found_mpi_names = [x.__name__ for x in found_mpi]

    if mo.options.showmpi:
        setLogLevelInfo()
        _logger.info("Found MPI classes %s" % (", ".join(found_mpi_names)))
        raise ExitException("Exit from showmpi")

    if mpi is None:
        mo.parser.print_shorthelp()
        mo.log.raiseException(("No MPI class found (scriptname %s; ismpirun %s). Please use mympirun through one "
                               "of the direct calls or make sure the mpirun command can be found. "
                               "Found MPI %s") % (scriptname, ismpirun, ", ".join(found_mpi_names)))
    else:
        mo.log.debug("Found MPI class %s (scriptname %s; ismpirun %s)" % (mpi.__name__, scriptname, ismpirun))

    sched = whatSched(getattr(mo.options, 'schedtype', None))
    if sched is None:
        mo.log.raiseException("No sched class found (options.schedtype %s)" % mo.options.schedtype)
    else:
        mo.log.debug("Found sched class %s from options.schedtype %s)" % (sched.__name__, mo.options.schedtype))

    class M(mpi, sched):
        """Temporary class to couple MPI and local sched"""
        def __init__(self, **kwargs):
            self.log = getLogger("%s_%s" % (mpi.__name__, sched.__name__))
            super(M, self).__init__(**kwargs)

    return M(options=mo.options, cmdargs=mo.args)


if __name__ == '__main__':
    ## TODO wrap in try/except
    try:
        m = getInstance()
        m.main()
        ec = 0
    except ExitException:
        ec = 0
    except:
        ## TODO: cleanup, only catch known exceptions
        if os.environ.get('MYMPIRUN_MAIN_EXCEPTION', 0) == '1':
            _logger.exception("Main failed")
        ec = 1

    sys.exit(ec)
