from pprint import pprint
# from recursivenamespace import recursivenamespace 
# or 
from recursivenamespace import rns

# I prefer to use as the following
results = rns(
    params=rns(
        alpha=1.0,
        beta=2.0,
    ),
    metrics=rns(
        accuracy=98.79,
        f1=97.62
    )
)
# I can access elements as dictionary keys or namespace attributes
print(results.params['alpha']) # 1.0
print(results['metrics'].accuracy) # 98.79



# I can convert just the metrics to dictionary
metrics_dict = results.metrics.to_dict()
print(metrics_dict) # {'accuracy': 98.79, 'f1': 97.62}

# Or I can convert all of it to a nested dictionary
output_dict = results.to_dict()
pprint(output_dict)
# {'metrics': {'accuracy': 98.79, 'f1': 97.62},
#  'params':  {'alpha': 1.0, 'beta': 2.0}}

# I can also flatten the keys using a separator
flat_dict = results.to_dict(flatten_sep='_')
pprint(flat_dict)
# {'metrics_accuracy': 98.79,
#  'metrics_f1': 97.62,
#  'params_alpha': 1.0,
#  'params_beta': 2.0}

# I can add more fields on the fly
results.experiment_name = 'experiment_name'
results.params.dataset_version = 'dataset_version'
results.params.gamma = 0.35

# If I add a key that contains '-' it will be converted to '_'
results.params['classifier-name'] = 'some-random-classifier'
print(results.params.classifier_name) # some-random-classifier
print(results.params['classifier-name'] == results.params['classifier-name'] == results.params.classifier_name) # True

