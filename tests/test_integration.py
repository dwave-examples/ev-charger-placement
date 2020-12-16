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
import re

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestDemo(unittest.TestCase):

    def test_smoke(self):
        """run demo.py and check that nothing crashes"""

        demo_file = os.path.join(project_dir, 'demo.py')
        subprocess.check_output([sys.executable, demo_file])

    def test_num_new_cs(self):
        """run demo.py and check that two new charging locations are found"""

        demo_file = os.path.join(project_dir, 'demo.py')
        value = subprocess.check_output([sys.executable, demo_file]).split()
        temp = ''.join([word.decode("utf-8") for word in value[6:10]])
        temp = re.findall(r'\d+', temp)
        res = list(map(int, temp))

        self.assertEqual(4, len(res))

    def test_solution_quality(self):
        """Run demo.py with seed set and check solution quality"""

        seed = '42'
        demo_file = os.path.join(project_dir, 'demo.py')
        value = subprocess.check_output([sys.executable, demo_file, "-s", seed]).split()

        # Check that new chargers aren't too close
        new_charger_dist = int(value[-1].decode("utf-8"))
        self.assertTrue(new_charger_dist > 10)

        # Check that new chargers are close to POIs
        temp = ''.join([word.decode("utf-8") for word in value[14:16]])
        poi_dist = re.findall(r'\d+', temp)
        poi_dist = list(map(int, poi_dist))
        poi_dist = poi_dist[0] + poi_dist[2]
        self.assertTrue(poi_dist < 18)

        # Check that new chargers are far from existing chargers
        temp = ''.join([word.decode("utf-8") for word in value[22:24]])
        old_cs_dist = re.findall(r'\d+', temp)
        old_cs_dist = list(map(int, old_cs_dist))
        old_cs_dist = old_cs_dist[0] + old_cs_dist[2]
        self.assertTrue(old_cs_dist > 15)

if __name__ == '__main__':
    unittest.main()