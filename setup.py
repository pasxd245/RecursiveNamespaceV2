from setuptools import setup, find_packages

setup(
    name='RecursiveNamespace', 
    version='0.2.0',  
    author='Hessam LA',
    author_email='hlotfali@purdue.edu',  
    description='Recursive Namespace. An extension of SimpleNamespace',  # A short description
    long_description=open('README.md').read(),  # Long description read from the readme
    long_description_content_type='text/markdown',  # Type of the long description
    url='https://github.com/HessamLa/RecursiveNamespace',  # Link to your package's GitHub repo or website
 
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    # packages=find_packages(where='.', include=['RecursiveNamespace']),  # Find all packages and subpackages
    install_requires=[  # List of dependencies
    ],
    classifiers=[  # Classifiers help users find your project
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum version requirement of the package
)