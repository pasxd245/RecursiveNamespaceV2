import unittest
from RecursiveNamespace.recursive_namespace import RecursiveNamespace

class TestRecursiveNamespace(unittest.TestCase):

    def test_basic_functionality(self):
        # Test basic functionality of RecursiveNamespace
        data = {'k1': 'v1', 'k2': {'k3': 'v3', 'k4': [100, 'v4']}}
        rn = RecursiveNamespace(data)
        self.assertEqual(rn.key1, 'v1')
        self.assertIsInstance(rn.key2, RecursiveNamespace)
        self.assertEqual(rn.key2.key3, 'v3')

    def test_flattening(self):
        # Test flattening of nested namespaces
        data = {'key1': {'key2': {'key3': 'value3', 'k4': 'v4'}}}
        rn = RecursiveNamespace(data)
        flat = rn.flatten()  # Assuming you have a flatten method
        self.assertEqual(flat, {'key1_key2_key3': 'value3', 'key1_key2_k4': 'v4'})

    # Add more tests as necessary for your class functionalities

if __name__ == '__main__':
    unittest.main()