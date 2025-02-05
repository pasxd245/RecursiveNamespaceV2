from setuptools import setup, find_packages
import versioneer

cmdclass = versioneer.get_cmdclass()

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    version=versioneer.get_version(),
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    cmdclass=cmdclass,
    package_dir={"": "src"},
    packages=find_packages(where="src"),
)
