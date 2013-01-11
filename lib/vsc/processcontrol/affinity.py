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
from .processcontrol import InitLog, ProcessControlBase

import ctypes

CPU_MASK_T_TYPE = ctypes.c_ulong

class CpuSetT(InitLog):
    """Class for the cpu bits from cpu_set_t struct
        based on vsc.utils.affinity cpu_set_t
    """
    CPUSETSIZE = ctypes.util.os.sysconf('SC_NPROCESSORS_CONF')
    NCPUBITS = 8 * ctypes.sizeof(CPU_MASK_T_TYPE)
    NBITMASK = CPUSETSIZE / NCPUBITS
    def __init__(self, *args, **kwargs):
        """
            - cpusetsize : maximum size of cpu_set_t (ie number of cores)
            - ncpubits : number of bits to represent cpu
            - nbitmask : number of cpubits in __bits
        """
        self.cpusetsize = kwargs.pop('cpusetsize', self.CPUSETSIZE)
        self.ncpubits = kwargs.pop('ncpubits', self.NCPUBITS)
        self.nbitmask = kwargs.pop('nbitmask', self.NBITMASK)
        super(CpuSetT, self).__init__(*args, **kwargs)

        self.bits = [None] * self.nbitmask
        self.cpus = [None] * self.cpusetsize

    def __str__(self):
        return self.convert_bits_hr()

    def convert_hr_bits(self, txt):
        """Convert human readable text into __bits
            eg 0-3,8,10-11 -> cpus = [0,1,1,1,0,0,0,1,0,1,1,0,..,0] -> __bits = [1678]
        """
        for cpu_range in txt.split(','):
            # always at least 2 elements: twice the same or start,end,start,end
            indices = [int(x) for x in cpu_range.split('-')] * 2

            # sanity check
            if indices[1] < indices[0]:
                self.log.error("convert_hr_bits: end is lower then start in '%s'" % cpu_range)
            elif indices[0] < 0:
                self.log.error("convert_hr_bits: negative start in '%s'" % cpu_range)
            elif indices[1] > self.cpusetsize + 1 :  # also covers start, since end > start
                self.log.error("convert_hr_bits: end larger then max %s in '%s'" % (self.cpusetsize, cpu_range))
            else:
                self.cpus[indices[0]:indices[1] + 1] = [1] * (indices[1] + 1 - indices[0])

        self.set_bits()
        self.log.debug("convert_hr_bits: converted %s into cpus %s (bits %s)" % (txt, self.cpus, self.bits))


    def convert_bits_hr(self):
        """Convert bits into human readable text"""
        if self.cpus is None:
            self.get_cpus()
        cpus_index = [idx for idx, cpu in enumerate(self.cpus) if cpu == 1]
        prev = -2  # not adjacent to 0 !
        parsed_idx = []
        for idx in cpus_index:
            if prev + 1 < idx:
                parsed_idx.append("%s" % idx)
            else:
                first_idx = parsed_idx[-1].split("-")[0]
                parsed_idx[-1] = "%s-%s" % (first_idx, idx)
            prev = idx
        return ",".join(parsed_idx)

    def get_cpus(self, bits=None):
        """Convert bits in list len == CPU_SETSIZE
            Use 1 / 0 per cpu
        """
        if bits is None:
            bits = self.bits
        cpuidx = 0
        for bitmask in bits:
            for idx in xrange(self.ncpubits):
                self.cpus[cpuidx] = bitmask & 1
                bitmask >>= 1
                cpuidx += 1
        return self.cpus

    def set_bits(self, bits=None):
        """Given self.cpus, set the bits"""
        if bits is None:
            bits = self.bits
        prev_cpus = self.cpus[:]
        for idx in xrange(self.nbitmask):
            cur_cpus = self.cpus[idx * self.ncpubits:(idx + 1) * self.ncpubits]
            cpus = [2 ** cpuidx for cpuidx, val in enumerate(cur_cpus) if val == 1]
            bits[idx] = sum(cpus)
        # sanity check
        if prev_cpus == self.get_cpus():
            self.log.debug("set_bits: new set to %s" % self.convert_bits_hr())
        else:
            # get_cpus() rescans
            max_shown = 20
            self.log.error("set_bits: something went wrong: previous cpus %s; current ones %s (first %d shown)" %
                           (prev_cpus[:max_shown], self.cpus[:max_shown], max_shown))

    def str_cpus(self):
        """Return a string representation of the cpus"""
        if self.cpus is None:
            self.get_cpus()
        return "".join(["%d" % x for x in self.cpus])

