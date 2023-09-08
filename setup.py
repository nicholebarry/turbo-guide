"""
Set up for sategazer
"""
from setuptools import setup, find_packages
import os

def get_requirements():
    """
    Read the requirements from a file
    """
    requirements = []
    requirements_filename = 'docs/python-requirements.txt'
    if os.path.exists(requirements_filename):
        with open(requirements_filename) as req:
            for line in req:
                # skip commented lines
                if not line.startswith('#'):
                    requirements.append(line.strip())
    return requirements

setup(
    name='FD_cloud_detection', # the name of the module
    description='Module that manages the cloud detection using the fluorescence telescopes at the Pierre Auger Observatory',
    author='Jason Ahumada',
    author_email='a1746103@adelaide.edu.au',
    url='https://github.com/nicholebarry/turbo-guide.git',
    packages=find_packages(where='src'), # the location of the module can also use find_packages()
    package_dir={'': 'src'},
    version='0.1',
    install_requires=get_requirements(),
    python_requires='>=3.8',
    scripts=['src/tools/runme'],
    entry_points={'console_scripts':['satellite_in_fov=sategazer.satellite_observation:main']}
)