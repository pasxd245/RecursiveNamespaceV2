from recursivenamespace import rns
from pprint import pprint

# You can pass a full dictionary to recursivenamespace
data = {
    'name': 'John Doe',
    'age': 30,
    'address': {
        'street': '123 Main St',
        'city': 'Anytown'
    }
}

print("------------")
print("data dictionary:")
pprint(data)

rn = rns(data)
print("------------")
print("rn:")
print(rn)

print("------------")
print("rn.name:", rn.name) # Output: John Doe
print("rn.address.street:", rn.address.street) # Output: 123 Main St

print("------------")
print("to_dict():")
pprint(rn.to_dict())

print("------------")
print("to_dict() flattening with '_' separator:")
pprint(rn.to_dict(flatten_sep='_'))


print("------------")
print("You can also use it as a dictionary:")
print(len(rn)) # 3
print(len(rn.address)) # 2
print(len(rn['address'])) # 2
print(rn.keys()) # ['name', 'age', 'address']
for k,v in rn.items():
    print(f"  {k}: {v}")

print("------------")
