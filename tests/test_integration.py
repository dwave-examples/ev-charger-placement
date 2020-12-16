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

        random.seed(42)
        demo_file = os.path.join(project_dir, 'demo.py')
        subprocess.check_output([sys.executable, demo_file])

    def test_num_new_cs(self):
        """run demo.py and check that two new charging locations are found"""

        demo_file = os.path.join(project_dir, 'demo.py')
        value = subprocess.check_output([sys.executable, demo_file])

        value = value.decode("utf-8") 
        temp = re.findall(r'\d+', value)
        res = list(map(int, temp))

        self.assertEqual(4, len(res))

if __name__ == '__main__':
    unittest.main()