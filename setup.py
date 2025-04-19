from setuptools import find_packages, setup

setup(
    name='serialdevicelib',
    packages=find_packages(include=['serialdevicelib']),
    version='0.1.0',
    description='tbc',
    author='bobisaperson1',
    install_requires=['socket', 'json']
)