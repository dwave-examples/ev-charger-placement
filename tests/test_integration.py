# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import sys
import unittest
import random
import demo
import neal

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestDemo(unittest.TestCase):

    def test_smoke(self):
        """run demo.py and check that nothing crashes"""

        demo_file = os.path.join(project_dir, 'demo.py')
        subprocess.check_output([sys.executable, demo_file])

    def test_scenario_setup(self):

        w, h = (random.randint(10,20), random.randint(10,20))
        num_poi, num_cs, num_new_cs = (random.randint(1,4), random.randint(1,4), random.randint(1,4))

        G, pois, charging_stations, potential_new_cs_nodes = demo.set_up_scenario(w, h, num_poi, num_cs)

        self.assertEqual(len(G.nodes()), w*h)
        self.assertEqual(len(pois), num_poi)
        self.assertEqual(len(charging_stations), num_cs)
        self.assertEqual(len(potential_new_cs_nodes), len(G.nodes())-len(charging_stations))

    def test_num_new_cs(self):
        """Check that correct number of new charging locations are found"""

        w, h = (random.randint(10,20), random.randint(10,20))
        num_poi, num_cs, num_new_cs = (random.randint(1,4), random.randint(1,4), random.randint(1,4))

        G, pois, charging_stations, potential_new_cs_nodes = demo.set_up_scenario(w, h, num_poi, num_cs)

        bqm = demo.build_bqm(potential_new_cs_nodes, num_poi, pois, num_cs, charging_stations, num_new_cs)

        sampler = neal.SimulatedAnnealingSampler()
        new_charging_nodes = demo.run_bqm_and_collection_solns(bqm, sampler, potential_new_cs_nodes)

        self.assertEqual(num_new_cs, len(new_charging_nodes))

    def test_close_to_pois(self):
        """run demo.py and with no existing charging stations and check that one
        new charging location is close to the centroid of the triangle"""

        w, h = (15, 15)
        num_poi, num_cs, num_new_cs = (3, 0, 1)

        _, pois, charging_stations, potential_new_cs_nodes = demo.set_up_scenario(w, h, num_poi, num_cs)

        pois = [(0,0),(6,14),(14,0)]
        centroid = (round((0+6+14)/3), round((0+14+0)/3))

        bqm = demo.build_bqm(potential_new_cs_nodes, num_poi, pois, num_cs, charging_stations, num_new_cs)

        sampler = neal.SimulatedAnnealingSampler()
        new_charging_nodes = demo.run_bqm_and_collection_solns(bqm, sampler, potential_new_cs_nodes)

        new_cs_x = new_charging_nodes[0][0]
        new_cs_y = new_charging_nodes[0][1]

        self.assertTrue(new_cs_x - centroid[0] < 4)
        self.assertTrue(new_cs_y - centroid[1] < 4)

    def test_solution_quality(self):
        """Run demo.py with seed set and check solution quality"""

        random.seed(42)
        w, h = (15, 15)
        num_poi, num_cs, num_new_cs = (0, 0, 2)

        _, pois, charging_stations, potential_new_cs_nodes = demo.set_up_scenario(w, h, num_poi, num_cs)

        bqm = demo.build_bqm(potential_new_cs_nodes, num_poi, pois, num_cs, charging_stations, num_new_cs)

        sampler = neal.SimulatedAnnealingSampler()
        new_charging_nodes = demo.run_bqm_and_collection_solns(bqm, sampler, potential_new_cs_nodes)

        _, _, new_cs_dist = demo.compute_soln_stats(pois, num_poi, charging_stations, num_cs, new_charging_nodes, num_new_cs)

        self.assertTrue(new_cs_dist > 15)

if __name__ == '__main__':
    unittest.main()