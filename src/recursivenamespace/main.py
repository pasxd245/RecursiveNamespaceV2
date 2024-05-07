# %%
import sys
from typing import Any
from types import SimpleNamespace

import collections

__all__ = ['recursivenamespace']

def flatten_dict(d, sep='_'):
    newd = {}
    for k,v in d.items():
        if(isinstance(v, dict)):
            flatd = flatten_dict(v, sep=sep)
            for k2,v2 in flatd.items():
                newd[f"{k}{sep}{k2}"] = v2
        else:
            newd[k] = v
    return newd

class recursivenamespace(SimpleNamespace):
    __VERSION__='0.0.4'
    def __init__(self,data={}, accepted_iter_types=[], **kwargs):
        self.__key_ = ''
        self.__supported_types_ = [list, tuple, set] + accepted_iter_types
        
        self.__protected_keys_ = ()
        self.__protected_keys_ = set(self.__dict__.keys())

        if(isinstance(data, dict)): kwargs.update(data)

        for key, val in kwargs.items():
            key = self.__re(key)
            if isinstance(val , dict):     
                val = recursivenamespace(**val)
                val.set_key(key)
            elif isinstance(val, recursivenamespace):
                val.set_key(key)
            else:
                val = self.__process(val)
            setattr(self, key, val)

    def __process(self, val):
        if isinstance(val, dict):
            return recursivenamespace(**val)
        elif isinstance(val, str):
            return val
        elif(hasattr(val, '__iter__') and type(val) in self.__supported_types_):
            lst = [self.__process(val=v) for v in val]
            try:
                return type(val)(lst)  # the type is assumed to support list-to-type conversion
            except Exception as e:
                print(f"Failed to make iterable object of type {type(val)}", e, out=sys.stderr)
                return val
        else:
            return val

    def __re(self, key):
        return key.replace('-','_')

    def set_key(self, key):
        self.__key_ = self.__re(key)
        
    def get_key(self):
        return self.__key_ 

    def update(self, data):
        try:
            if(not isinstance(data, recursivenamespace)):
                data = recursivenamespace(data)
        except Exception as e:
            raise Exception(f"Failed to update with data of type {type(data)}")
        for key, val in data.items():
            self[key] = val

    def __remove_protected_key(self, key):
        self.__protected_keys_.remove(key) 
        self.__dict__.pop(key)
        
    def __eq__(self, other):
        if isinstance(other, recursivenamespace):
            return vars(self) == vars(other)
        elif isinstance(other, dict):
            return vars(self) == other
        return False
        
    def __repr__(self) -> str:
        s = ''
        for k,v in self.items():
            s += f'{k}={v}, '
        if(len(s)>0):   s = s[:-2] # remove the last ', '
        s = f"RNS({s})"
        return s

    def __str__(self) -> str:
        return self.__repr__()
    
    def __len__(self):
        return len(self.__dict__) - len(self.__protected_keys_)

    def __delattr__(self, key):
        key = self.__re(key)
        if(key not in self.__protected_keys_):
            # delattr(self, key)
            del self.__dict__[key]

    def __setitem__(self, key: str, value: Any):
        key = self.__re(key)
        if(key in self.__protected_keys_):
            raise KeyError(f"The key '{key}' is protected.")
        setattr(self, key, value)

    def __getitem__(self, key):
        key = self.__re(key)
        if(key in self.__protected_keys_):
            raise KeyError(f"The key '{key}' is protected.")
        return  getattr(self, key)

    def __delitem__(self, key):
        key = self.__re(key)
        delattr(self, key)

    def __contains__(self, key):
        key = self.__re(key)
        return key in self.__dict__
    
    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def copy(self):
        return self.__copy__()
    
    def deepcopy(self):
        return self.__deepcopy__()
    
    def pop(self, key, default=None):
        key = self.__re(key)
        if(key in self.__protected_keys_):
            raise KeyError(f"The key '{key}' is protected.")
        if key in self.__dict__:
            val = self.__dict__[key]
            del self.__dict__[key]
            return val
        else: return default
    
    def items(self):
        return [(k,v) for k,v in self.__dict__.items() if k not in self.__protected_keys_]
    
    def keys(self):
        return [k for k in self.__dict__.keys() if k not in self.__protected_keys_]
    
    def values(self):
        return [v for k,v in self.__dict__.items() if k not in self.__protected_keys_]
    
    def __iter__(self):
        if(sys._getframe(1).f_code.co_name=='dict'):
            return self.to_dict()
        return iter(self.keys())

    def to_dict(self, flatten_sep:str=False):
        """Convert the recursivenamespace object to a dictionary.
        If flatten_sep is not False, then the keys are flattened using the separator.
        """
        pairs = []
        for k,v in self.items():
            if isinstance(v, recursivenamespace):
                pairs.append((k, v.to_dict()))
            elif isinstance(v, dict):
                pairs.append((k, v))
            elif hasattr(v, '__iter__') and type(v) in self.__supported_types_:
                pairs.append((k, self.__iter_to_dict(v)))
            else:
                pairs.append((k, v))
        d = dict(pairs)
        if(flatten_sep):
            d = flatten_dict(d, sep=flatten_sep)
        return d
    
    def __iter_to_dict(self, iterable=None):
        elements = []
        for val in iterable:
            if isinstance(val, recursivenamespace):
                elements.append(val.to_dict())
            elif isinstance(val, dict):
                elements.append(val)
            elif hasattr(val, '__iter__') and type(val) in self.__supported_types_:
                elements.append(self.__iter_to_dict(val))
            else:
                elements.append(val)
        return type(iterable)(elements)
    
if __name__ == '__main__':
    print("rname1 = recursivenamespace(a=1, b=2,c=recursivenamespace(d=3, e=444))")
    rname1 = recursivenamespace(a=1, b=2,c=recursivenamespace(d=3, e='444'))
    print("rname2 = recursivenamespace({'a':1, 'b':2, 'c':{'d':3, 'e':444}})")
    rname2 = recursivenamespace({'a':1, 'b':2, 'c':{'d':3, 'e':'444'}})

    print(rname1)
    print(rname2)
    assert rname1 == rname2

    data = {
        '11':11,
        'a-': 1, 
        'b': (2,3), 
        'c': [4,{'c5':'555'}],
        'd': set([6,'7',8]),
        'e': {
            'e_1': 9, 
            'e_2': {
                    'e_2_1': 10, 
                    'e_2_2': (11,)
                    },
            'e_3': [12,13]}
    }
    rname = recursivenamespace(data)
    print('dict(rname)')
    print(dict(rname))
    data2 = rname.to_dict()
    print(data)
    print(data2)

    print("Flatten")
    print(rname)
    from pprint import pprint
    pprint(rname.to_dict(flatten_sep='__'))
# %%
    print(rname)
    print('%20s :'%(type(rname.a_)), rname.a_)
    print('%20s :'%(type(rname.b)), rname.b)
    print('%20s :'%(type(rname.c)), rname.c)
    print('%20s :'%(type(rname.d)), rname.d)
    print('%20s :'%(type(rname.e.e_2.e_2_2)), rname.e.e_2.e_2_2)
    print('%20s :'%(type(rname.c[1].c5)), rname.c[1].c5)
    rname['new_obj'] = 100
    print('%20s :'%(type(rname.new_obj)), rname.new_obj)
    rname.newdict = {'new1':1, 'new2':2}
    print('%20s :'%(type(rname.newdict)), rname.newdict)
    print(rname.e)
    print(rname.e.e_1)
    print(rname.e.e_2.e_2_2)
    print("----------------------------")
    print(rname.e.e_2.get_key())
    

    print("\nShow values in rname, without recursion:")
    for v in rname:
        print(v)

    rname.key1 = 'someval'
    rname['key2'] = 'someval'
    assert rname['key1'] == rname.key2

    del rname.key1 # delete an item
    assert 'key1' not in rname
    
    rname.pop('key2') # delete an item
    assert 'key2' not in rname

    rname.dict1 = {'a':1, 'b':2}
    print(type(rname.dict1), rname.dict1)

    rname.dict2 = recursivenamespace({'a':1, 'b':2})
    print(type(rname.dict2), rname.dict2)

    assert rname.dict1 != rname.dict2
    assert rname.dict1['a'] == rname.dict2.a

    

    import pickle
    pklpath  = '/tmp/test.pkl'
    # pickel test
    with open(pklpath, 'wb') as f:
        pickle.dump(rname, f)
    with open(pklpath, 'rb') as f:
        rname2 = pickle.load(f)

    print()
    print("Result after unpickling")
    print(rname2.e)
    print(rname2.e.e_1)
    print(rname2.e.e_2.e_2_2)

    print()
    print("rname == rname2:", rname == rname2)

    print(rname.to_dict())

if __name__=='__main__':
    pass

