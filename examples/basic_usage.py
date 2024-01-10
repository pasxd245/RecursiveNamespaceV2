from pprint import pprint
from RecursiveNamespace import RecursiveNamespace as RN

# I prefer to use as the following
results = RN(
    params=RN(
        alpha=1.0,
        beta=2.0,
        dataset_name='dataset_name',
        dataset_path='dataset_path',
        classifier_name='classifier_name',
    ),
    metrics=RN(
        accuracy=0.0,
        f1=0.0,
    )
)

print(results.params.k1)
print(results.metrics.accuracy)
# then I can add more information on the fly
results.experiment_name = 'experiment_name'
results.params.dataaset_version = 'dataset_version'
results.params.gamma = 3.0

# Then I'd convert it to dictionary
output_dict = results.to_dict()

# or just convert metrics to dictionary
metrics_dict = results.metrics.to_dict()

# You can also pass a full dictionary to RecursiveNamespace
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

rn = RN(data)
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
rn.scores = RN({'score-1': 98.4, 'score-2': 100})
print(f"rn.scores.score_1: {rn.scores.score_1}")
print(f"rn.scores.score_2: {rn.scores.score_2}")
rn.scores.score_3 = 99.07
print(f"rn.scores.score_3: {rn.scores.score_3}")

# I personally would like to use it like the following
