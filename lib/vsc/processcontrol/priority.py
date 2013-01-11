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
A module to abstract scheduler priority
"""

from .processcontrol import ProcessControlBase

class Priority(ProcessControlBase):
    """A class to provide shceduler control"""
    PRIO_MIN = -20
    PRIO_MAX = 20
    PRIO_DEFAULT = 0

    def _sanitize_range(self, prio):
        """Check if prio is in valid range
            prio : int
            @return : int (MIN<x<MAX)
        """
        if prio < self.PRIO_MIN:
            self.log.debug("_sanitize_range: prio %d lower then minimum %d" % (prio, self.PRIO_MIN))
            prio = self.PRIO_MIN
        elif prio > self.PRIO_MAX:
            self.log.debug("_sanitize_range: prio %d higher then maximum %d" % (prio, self.PRIO_MAX))
            prio = self.PRIO_MAX

        return prio

    def get_priority(self):
        """Get the priority value
            @return : int
            TO BE IMPLEMENTED
        """
        self.log.error("get_priority not implemented")

    def _set_priority(self, newprio):
        """actual priority setting with sanitized newprio
            - newprio : int
            TO BE IMPLEMENTED
        """
        self.log.error("_set_priority not implemented")

    def set_priority(self, newprio):
        """Set the priority
            newprio : int
        """
        prio = self._sanitize_range(prio)
        self._set_priority(prio)
