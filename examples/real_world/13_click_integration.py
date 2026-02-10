"""
Click is a usefull package for developing CLIs. Nevertheless, use strings
as dictionary keys were not much appealing to me.
Using the RecursiveNamespace package, now the click is much sexier to me.

Example:
$ python click_package.py evaluate --train_size 0.77
--------
Input parameters
 train_size: 0.77
 test_size:  0.22999999999999998
 classifier: rf
-------
Prediction parameters.
 train size: 0.77
 classifier: rf
--------
Iterating over results:
 accuracy  :   0.9800
 f1_score  :   0.9700
--------
Accessing results from RNS through dictionary keys
 accuracy :   0.9800
 f1       :   0.9700
--------
Accessing results from RNS through namespaces
 accuracy :   0.9800
 f1       :   0.9700
"""

import click

from recursivenamespace import RNS


@click.group()
def cli():
    """cli"""
    pass


def predict(train_size, classifier, **kwargs):
    print("-------")
    print("Prediction parameters.")
    print(f" train size: {train_size:.2f}")
    print(f" classifier: {classifier}")
    acc = 0.98
    f1 = 0.97
    return RNS(accuracy=acc, f1_score=f1)


@cli.command()
@click.option("--train_size", default=0.1, help="Size of the dataset")
@click.option("--test_size", default=None, help="Size of the dataset")
@click.option(
    "--classifier",
    type=click.Choice(["lr", "rf", "ada"]),
    default="rf",
    help="The Classifier model. rf: Random Forest, lr: Logistic Regression, ada: AdaBoost.",
)
def evaluate(**options):
    """Evaluate the model."""
    # LET'S GET THE PARTY STARTED
    options = RNS(options)

    if options.test_size is None:
        options.test_size = 1.0 - options.train_size
    else:
        options.train_size = 1.0 - options.test_size
    print("--------")
    print("Input parameters")
    print(" train_size:", options.train_size)
    print(" test_size: ", options.test_size)
    print(" classifier:", options.classifier)

    results = predict(**options)  # returns RNS type

    print("--------")
    print("Iterating over results:")
    for (
        k,
        v,
    ) in (
        results.items()
    ):  # results is RNS type. But you can treat is as dictionary.
        print(f" {str(k):<10s}: {v:8.4f}")

    # OR you could use the namespace style
    print("--------")
    print("Accessing results from RNS through dictionary keys")
    print(f" accuracy : {results['accuracy']:8.4f}")
    print(f" f1       : {results['f1_score']:8.4f}")
    # OR you could use the namespace style
    print("--------")
    print("Accessing results from RNS through namespaces")
    print(f" accuracy : {results.accuracy:8.4f}")
    print(f" f1       : {results.f1_score:8.4f}")


if __name__ == "__main__":
    cli()
