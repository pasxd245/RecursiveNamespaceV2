from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='RecursiveNamespace', 
    version='0.2.02',  
    author='Hamidreza Lotfalizadeh (Hessam)',
    author_email='HLOTFALI_at_PURDUE_EDU@random.site',  
    description='Recursive Namespace. An extension of SimpleNamespace',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/HessamLa/RecursiveNamespace', 
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=[],
    classifiers=[  
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)