from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in asa/__init__.py
from asa import __version__ as version

setup(
	name="asa",
	version=version,
	description="Amanaki STEM Academy",
	author="Senituli Taumoepeau",
	author_email="senitaumoepeau@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
