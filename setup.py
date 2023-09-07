"""
Set up for Sategazer
"""
from setuptools import setup, find_packages
import os

def get_requirements():
    """
    Read the requirements from a file
    """
    requirements = []
    if os.path.exists('requirements.txt'):
        with open('requirements.txt') as req:
            for line in req:
                # skip commented lines
                if not line.startswith('#'):
                    requirements.append(line.strip())
    return requirements

setup(
    name='Sategazer', # the name of the module
    packages=['src.Sategazer'], # the location of the module can also use find_packages()
    version='0.1',
    install_requires=get_requirements(),
    python_requires='>=3.8',
    scripts=['src/tools/runme'],
    entry_points={'console_scripts':['satellite_in_fov=src.Sategazer.stargazer:main']}
)