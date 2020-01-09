from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = ['tqdm>=4.40.2', 'librosa>=0.7.1', 'unidecode>=1.1.1', 'inflect>=3.0.2', 'matplotlib']
#['some_PyPI_package>=1.5',
#                     'another_package==2.6']

setup(
    name='trainer',
    version='0.1',
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    description='My training application package.'
)
