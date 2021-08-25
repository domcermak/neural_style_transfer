# https://www.cosmicpython.com/book/appendix_project_structure.html

from setuptools import setup, find_packages
from pathlib import Path


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    line_iter = (line.strip() for line in open(filename))
    return [line for line in line_iter if line and not line.startswith("#")]


requirements_file_path = str(Path(__file__).absolute().parent.parent) + '/requirements.txt'
install_reqs = parse_requirements(requirements_file_path)

setup(
    name="neural_style_transfer",
    version="0.1",
    packages=find_packages(include=['neural_style_transfer', 'neural_style_transfer.*']),
    install_requires=install_reqs,
)
