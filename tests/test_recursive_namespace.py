import unittest
from recursivenamespace import recursivenamespace as rn


class TestRecursiveNamespace(unittest.TestCase):
    def test0(self):
      data = {'k1': 'value1', 'k-2': {'k3': 'value3', 'k4': [100, 'value4']}}    
      rn1 = rn(data)
      rn2 = rn(k1='value1', k_2=rn({'k3': 'value3', 'k4': [100, 'value4']}))
      self.assertEqual(rn1, rn2)
      print(rn1)

    def test_basic_functionality(self):
        data = {'k1': 'v1', 'k-2': {'k3': 'v3', 'k4': [100, 'v4']}}
        r = rn(data)
        self.assertEqual(r.k1, 'v1')
        self.assertEqual(r.k_2, r['k-2'])
        self.assertEqual(r.k_2, r['k_2'])
        self.assertIsInstance(r.k_2, rn)
        self.assertEqual(r.k_2.k3, 'v3')

    def test_equal(self):
        # Test basic functionality of recursivenamespace
        print("rname1 = recursivenamespace(a=1, b=2,c=recursivenamespace(d=3, e=4))")
        rname1 = rn(a=1, b=2,c=rn(d=3, e='404'))
        print("rname2 = recursivenamespace({'a':1, 'b':2, 'c':{'d':3, 'e':'404'}})")
        rname2 = rn({'a':1, 'b':2, 'c':{'d':3, 'e':'404'}})
        print(rname1)
        print(rname2)
        assert rname1 == rname2

    def test_to_dict(self):
        # Test flattening of nested namespaces
        data = {'key1': {'key2': {'key3': 'value3', 'k4': 'v4'}}}
        rn0 = rn(data)
        d = rn0.to_dict()  # Assuming you have a flatten method
        print(d)
        self.assertEqual(d, data)
    
    def test_to_dict_flatten(self):
        # Test flattening of nested namespaces
        data = {'key1': {'key2': {'key3': 'value3', 'k4': ['v4', 'v5']}}}
        rn0 = rn(data)
        d = rn0.to_dict(flatten_sep='_')
        self.assertEqual(d, {'key1_key2_key3': 'value3', 'key1_key2_k4': ['v4', 'v5']})

    # Add more tests as necessary for your class functionalities

if __name__ == '__main__':
    unittest.main()