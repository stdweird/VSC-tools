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
A module to abstract cpu affinity interfaces
"""
from .processcontrol import ProcessControlBase, what_classes
from .cpusett import CpuSetT

def what_affinity(name=None):
    """What affinity classes are there?"""
    found_affinities = what_classes(Affinity)

    # case insensitive match?
    if name is not None:
        found_affinities = [x for x in found_affinities if x.is_affinity(name)]

    return found_affinities


class Affinity(ProcessControlBase):
    """An abstract class for controlling cpu affinity of a process"""
    AFFINITY_MODE = None
    AFFINITY_ALGORITHM = None
    CPUSETT_CLASS = CpuSetT

    def __init__(self, *args, **kwargs):
        super(Affinity, self).__init__(*args, **kwargs)

        self.cpusett = self.CPUSETT_CLASS()

    @classmethod
    def is_affinity(self, cls, name):
        return name.lower() == cls.AFFINITY_MODE.lower()

    @classmethod
    def is_algorithm(self, cls, name):
        return name.lower() == cls.AFFINITY_ALGORITHM.lower()

    def _get_affinity(self):
        """Actually get the affinity of self.pid and save in self.cpusett
        """
        self.log.error("_get_affinity not implemented")

    def _set_affinity(self):
        """Actually set the affinity for self.pid from self.cpusett
            TO BE IMPLEMENTED
        """
        self.log.error("_set_affinity not implemented")

    def _sanitize_cpuset(self, cpuset=None):
        """Check if cpuset is proper type"""
        if cpuset is None:
            cpuset = self.cpusett

        if not isinstance(cpuset, self.CPUSETT_CLASS):
            self.log.error("_sanitize_cpuset: cpuset type %s, expected %s" % (type(cpuset), self.CPUSETT_CLASS.__name__))

        # TODO actual sanity check

        self.cpusett = cpuset

    def get_affinity(self):
        """Get the affinity of self.pid
            @return : CpuSetT instance
        """
        self._get_affinity()
        return self.cpusett

    def set_affinity(self, cpuset):
        """Set the affinity for self.pid
            - cpuset : instance of CpuSetT
        """
        self._sanitize_cpuset(cpuset)
        self._set_affinity()

    def _algorithm(self, *args, **kwargs):
        """Given set of arguments, set cpusett with new process placement
            TO BE IMPLEMENTED
        """
        self.log.error("_algorithm not implemented")

    def algorithm(self, *args, **kwargs):
        """Given set of arguments, set cpusett with new process placement
            TO BE IMPLEMENTED
        """
        self._algorithm(*args, **kwargs)
        self.set_affinity(self.cpusett)
