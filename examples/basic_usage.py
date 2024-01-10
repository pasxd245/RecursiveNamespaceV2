from pprint import pprint
from RecursiveNamespace import RecursiveNamespace

# Creating a simple recursive namespace
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

rn = RecursiveNamespace(data)
print("------------")
print("rn:")
print(rn)

print("------------")
print("rn.name:", rn.name) # Output: John Doe
print("rn.address.street:", rn.address.street) # Output: 123 Main St

print("------------")
print("to_dict():")
print(rn.to_dict())

print("------------")
print("to_dict() flattening with '_' separator:")
print(rn)
pprint(rn.to_dict(flatten_sep='_'))


print("------------")
rn.scores = RecursiveNamespace({'score-1': 98, 'score-2': 100})
print(f"rn.scores.score_1: {rn.scores.score_1}")
print(f"rn.scores.score_2: {rn.scores.score_2}")
rn.scores.score_3 = 99
print(f"rn.scores.score_3: {rn.scores.score_3}")