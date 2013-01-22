#
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
from unittest import TestCase, TestLoader
from vsc.processcontrol.cpusett import CpuSetT
from vsc.processcontrol.algorithm import BasicCore

TOTAL_CORES = len([x for x in open('/proc/cpuinfo').readlines() if x.lower().startswith('processor')])

class TestCpuSetT(CpuSetT):
    DEFAULT_CPUSETSIZE = 16  # set high enough
    DEFAULT_NCPUBITS = 8  # default c_ulong is 8 bytes, this is just for test

class ProcesscontrolTest(TestCase):
    """Tests for vsc.processcontrol"""

    def test_cpusett(self):
        """Test CpuSetT class"""
        cs = TestCpuSetT()
        cs.convert_hr_bits('2,5-8,10,11-11')
        self.assertEqual(cs.nbitmask, 2)
        self.assertEqual(cs.cpusetsize, 16)
        self.assertEqual(cs.cpus[:cs.DEFAULT_CPUSETSIZE], [0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0])
        self.assertEqual(cs.bits, [228, 13])

        cs.set_bits([1, 0, 0, 1, 1, 1, 0, 0, 0, 1])
        self.assertEqual(len(cs.cpus), cs.cpusetsize)
        self.assertEqual(cs.bits, [57, 2])
        self.assertEqual(cs.convert_bits_hr(), "0,3-5,9")

    def test_basiccore(self):

        bc = BasicCore()

        # 4 total cpus, 4 processes to place
        bc.create(4, 4)
        self.assertEqual(bc.proc_placement, [[0], [1], [2], [3]])

        # 8 total cpus, 4 processes to place
        bc.create(8, 4)
        self.assertEqual(bc.proc_placement, [[0], [0], [1], [1], [2], [2], [3], [3]])

        # 4 total cpus, 8 processes to place
        bc.create(4, 8)
        self.assertEqual(bc.proc_placement, [[0, 1], [2, 3], [4, 5], [6, 7]])

        # 6 total cpus, 4 processes to place
        bc.create(6, 4)
        self.assertEqual(bc.proc_placement, [[0], [0], [1], [2], [2], [3]])

        # 6 total cpus, 8 processes to place
        bc.create(6, 8)
        self.assertEqual(bc.proc_placement, [[0], [1], [2, 3], [4], [5], [6, 7]])

def suite():
    """ returns all the testcases in this module """
    return TestLoader().loadTestsFromTestCase(ProcesscontrolTest)

if __name__ == '__main__':
    """Use this __main__ block to help write and test unittests
        just uncomment the parts you need
    """
#    cs = TestCpuSetT()
#    cs.convert_hr_bits('2,5-8,10,11-11')
#    print cs.nbitmask
#    print cs.cpusetsize
#    print cs.cpus[:cs.DEFAULT_CPUSETSIZE]
#    print cs.bits

    bc = BasicCore()

    # 4 total cpus, 4 processes to place
    bc.create(4, 4)
    print bc.proc_placement

    # 8 total cpus, 4 processes to place
    bc.create(8, 4)
    print bc.proc_placement

    # 4 total cpus, 8 processes to place
    bc.create(4, 8)
    print bc.proc_placement

    # 6 total cpus, 4 processes to place
    bc.create(6, 4)
    print bc.proc_placement

    # 6 total cpus, 8 processes to place
    bc.create(6, 8)
    print bc.proc_placement
