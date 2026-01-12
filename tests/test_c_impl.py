import unittest
import subprocess
import json
import os
import sys

class TestCImplementation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Compile the C code
        src_dir = os.path.join(os.getcwd(), 'src', 'gollyx_c')
        subprocess.check_call(['make'], cwd=src_dir)
        cls.executable = os.path.join(src_dir, 'gollyx_c')

    def run_c_sim(self, json_path):
        result = subprocess.run(
            [self.executable, json_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(result.stderr)
        self.assertEqual(result.returncode, 0, "C simulation failed")
        return json.loads(result.stdout)

    def test_toroidal_simulation(self):
        # uses src/gollyx_c/test_toroidal.json generated earlier
        json_path = os.path.join(os.getcwd(), 'src', 'gollyx_c', 'test_toroidal.json')
        output = self.run_c_sim(json_path)
        
        # Expected values from tests/test_toroidal.py test_life_150_240_stoppingcriteria_280
        self.assertEqual(output['generation'], 3364)
        self.assertEqual(output['liveCells'], 689)
        self.assertEqual(output['liveCells1'], 132)
        self.assertEqual(output['liveCells2'], 557)
        self.assertTrue(output['found_victor'])
        self.assertEqual(output['who_won'], 2)

    def test_star_simulation(self):
        # uses src/gollyx_c/test_star.json generated earlier (Flying V2)
        json_path = os.path.join(os.getcwd(), 'src', 'gollyx_c', 'test_star.json')
        output = self.run_c_sim(json_path)
        
        # Expected values from tests/test_star.py test_flying_v2_122_222
        self.assertEqual(output['generation'], 1138)
        self.assertEqual(output['liveCells'], 87)
        self.assertEqual(output['liveCells1'], 20)
        self.assertEqual(output['liveCells2'], 67)

if __name__ == '__main__':
    unittest.main()
