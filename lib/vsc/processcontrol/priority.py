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

from .processcontrol import ProcessControlBase, what_classes


def what_priority(name=None):
    """What priority classes are there?"""
    found_priorities = what_classes(Priority)

    # case insensitive match?
    if name is not None:
        found_priorities = [x for x in found_priorities if x.is_priority_name(name)]

    return found_priorities


class Priority(ProcessControlBase):
    """A class to provide scheduler control"""
    PRIORITY_MODE = None

    PRIO_MIN = -20
    PRIO_MAX = 20
    PRIO_DEFAULT = 0
    def __init__(self, *args, **kwargs):
        super(Priority, self).__init__(*args, **kwargs)

        self.priority = self.PRIO_DEFAULT

    @classmethod
    def is_priority_name(self, cls, name):
        return name.lower() == cls.PRIORITY_MODE.lower()

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

        self.priority = prio

    def _get_priority(self):
        """Get the priority value of self.pid and store in self.priority
            TO BE IMPLEMENTED
        """
        self.log.error("get_priority not implemented")

    def _set_priority(self):
        """actual priority setting with sanitized self.priority
            TO BE IMPLEMENTED
        """
        self.log.error("_set_priority not implemented")

    def get_priority(self):
        """Get the priority value of self.pid
            @return : int
        """
        self._get_priority()
        self._sanitize_range(self.priority)
        return self.priority


    def set_priority(self, newprio):
        """Set the priority of self.pid
            newprio : int
        """
        self._sanitize_range(newprio)
        self._set_priority()
