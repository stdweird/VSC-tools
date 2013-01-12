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
Some core parts for cpu pin placement algorithms
"""
from .processcontrol import InitLog

class Algorithm(InitLog):
    """Compute the process placement on a given number of cpus. Result is
    in proc_placement, a list of lists with size total cpus available
    """

    def __init__(self, *args, **kwargs):
        self.proc_placement = None
        super(Algorithm, self).__init__(*args, **kwargs)

    def get_cpus(self, process_idx):
        """Find all cpus that process_idx can use from proc_placement"""
        return [idx for idx, proc_cpuidx in enumerate(self.proc_placement) if process_idx in proc_cpuidx]

    def create(self, *args):
        """Create the proc_placement
            TO BE  IMPLEMENTED
        """
        self.log.error('create: need to be implemented')

class BasicCore(Algorithm):
    def create(self, total_cpus, total_processes):
        """Basic core pinning.
            - total_cpus : total number of cores that can be used (eg limited by cgroup)
            - total_processes : number of processes to be distributed over total_cpus
            - process_idx : process index in range of total_processes

        This algorithm will attempt to do packed placement for oversubscribed processes
        (e.g. if 2 cores are available for 4 processes, processes 0 and 1 will be pinned on core 0 and
        processes 2 and 3 on core 1).

        The algorithm will attempt to group cores for same process and not share if not needed (e.g.
        for 4 cores available and 3 process the placment will be [[0],[0],[1],[2]] rather then [[0],[0,1],[1],[2]]).

        Division algorithm is from
        http://stackoverflow.com/questions/8084010/algorithm-for-subdividing-an-array-into-semi-equal-uniform-sub-arrays
        """
        def make_div(N, M):
            """
            Number of processes (total N) to place on M cpus
            >>> x(12,6)
            [2, 2, 2, 2, 2, 2]
            >>> x(6,12)
            [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
            >>> x(12,12)
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            >>> x(8,12)
            [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1]
            """
            # / has to be integer division
            return [(N * i + N) / M - (N * i) / M for i in xrange(M)]

        distrib = make_div(total_processes, total_cpus)
        self.proc_placement = []

        current_proc = 0
        for cpu_idx, nr_ppc in enumerate(distrib):
            new_cpu = []
            if nr_ppc == 0:
                # 0 has special meaning : no processes on this cpu means the current process can use it
                new_cpu.append(current_proc)
            else:
                for idx in xrange(nr_ppc):
                    new_cpu.append(current_proc)
                    current_proc += 1
            self.proc_placement.append(new_cpu)

        # sanity
        if not current_proc == total_processes:  # last current_proc is +1
            self.log.error("create: problem with placement")


