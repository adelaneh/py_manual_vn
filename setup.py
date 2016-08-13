from setuptools import setup

setup(name='py_valuenormazliation',
	version='0.1',
	description='Attribute value normalization tool',
	long_description='This package provides the neccessary workflow and interface to normalize a set of (attribute) values of type character string.',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python :: 2.7',
		'Topic :: Data Cleaning :: Databases :: Data Management',
		],
	keywords='value normalization data cleaning management',
	url='http://github.com/adelaneh/py_valuenormazliation',
	author='Adel Ardalan',
	author_email='adel@cs.wisc.edu',
	license='MIT',
	packages=['py_valuenormazliation'],
#	install_requires=[
#		'PyQt4',
#		],
	include_package_data=True,
	zip_safe=False)
