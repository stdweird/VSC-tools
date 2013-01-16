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
import ctypes
import ctypes.util
from .processcontrol import InitLog

class CpuSetT(InitLog):
    """Class for the cpu bits from cpu_set_t struct
    Class is based on vsc.utils.affinity cpu_set_t
    """
    DEFAULT_BIT=0

    CPU_MASK_T_TYPE = ctypes.c_ulong
    DEFAULT_CPUSETSIZE = ctypes.util.os.sysconf('SC_NPROCESSORS_CONF')
    DEFAULT_NCPUBITS = 8 * ctypes.sizeof(CPU_MASK_T_TYPE)

    def __init__(self, *args, **kwargs):
        """
        Supported arguments
            - cpusetsize : maximum size of cpu_set_t (ie number of cores)
            - ncpubits : number of bits to represent cpu
            - nbitmask : number of cpubits in __bits
        """
        nbitmask, remain = divmod(self.DEFAULT_CPUSETSIZE, self.DEFAULT_NCPUBITS)
        if remain > 0:
            # this makes that nbitmask is always at least 1
            nbitmask += 1

        self.cpusetsize = kwargs.pop('cpusetsize', self.DEFAULT_NCPUBITS * nbitmask)
        self.ncpubits = kwargs.pop('ncpubits', self.DEFAULT_NCPUBITS)
        self.nbitmask = kwargs.pop('nbitmask', self.cpusetsize / self.ncpubits)

        super(CpuSetT, self).__init__(*args, **kwargs)

        # default no cores selected
        self.bits = [self.DEFAULT_BIT] * self.nbitmask
        self.cpus = [self.DEFAULT_BIT] * self.cpusetsize

    def __str__(self):
        return self.convert_bits_hr()

    def convert_hr_bits(self, txt):
        """Convert human readable text into __bits
        E.g. string  '0-3,8,10-11' -> cpus = [0,1,1,1,0,0,0,1,0,1,1,0,..,0] -> bits = [[1678],..]

        Text can also be int/long or list/tuple
        """
        if isinstance(txt, (int, long,)):
            txt = "%d" % txt
        elif isinstance(txt, (list, tuple,)):
            txt = ",".join(["%s" % x for x in txt])

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
        cpus_index = self.get_cpus_idx()
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

    def set_cpus(self,cpus_list):
        """Given list, set it as cpus"""
        nr_cpus = len(cpus_list)
        if  nr_cpus > self.cpusetsize:
            self.log.error("set_cpus: length cpu list %s is larger then cpusetsize %s. Truncating to cpusetsize" %
                           (nr_cpus , self.cpusetsize))
            cpus_list = cpus_list[:self.cpusetsize]
        elif nr_cpus < self.cpusetsize:
            cpus_list.extend([self.DEFAULT_BIT] * (self.cpusetsize - nr_cpus))

        self.cpus = cpus_list

    def get_cpus(self, bits=None):
        """Convert bits to list with length self.cpusetsize
        Set 0 or 1 for each cpu according to bitmask
        """
        if bits is None:
            bits = self.bits
        cpuidx = 0
        for bitmask in bits:
            for idx in xrange(self.ncpubits):
                self.cpus[cpuidx] = bitmask & 1
                bitmask >>= 1
                cpuidx += 1
        if not cpuidx == self.cpusetsize:  # no -1 , last step does cpuidx+1
            self.log.error("get_cpus: unexpected final index %s (expected %s)" % (cpuidx, self.cpusetsize - 1))
        if not len(self.cpus) == self.cpusetsize:
            self.log.error("get_cpus: unexpected length for cpus %s (expected %s)" % (len(self.cpus), self.cpusetsize))

        return self.cpus

    def get_cpus_idx(self):
        """Get the cpus by idx"""
        return [idx for idx, cpu in enumerate(self.cpus) if cpu == 1]

    def set_bits(self, cpus=None):
        """Given self.cpus, set the bits"""
        if cpus is not None:
            self.set_cpus(cpus)
        prev_cpus = self.cpus[:]
        for idx in xrange(self.nbitmask):
            cur_cpus = self.cpus[idx * self.ncpubits:(idx + 1) * self.ncpubits]
            self.bits[idx] = sum([2 ** cpuidx for cpuidx, val in enumerate(cur_cpus) if val == 1])

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

