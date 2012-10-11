from setuptools import setup
from jsonConfig import __version__ as version
import os.path

descr_file = os.path.join( os.path.dirname( __file__ ), 'README' )

setup( 
    name = 'jsonConfig',
    version = version,

    packages = ['jsonConfig'],

    description = 'Sparse JSON based config files with GUI editor.',
    long_description = open( descr_file ).read(),
    author = 'Ryan Hope',
    author_email = 'rmh3093@gmail.com',
    url = 'https://github.com/RyanHope/jsonConfig',
    classifiers = [
				'License :: OSI Approved :: GNU General Public License (GPL)',
				'Programming Language :: Python :: 2',
				'Topic :: Utilities',
    ],
	license = 'GPL-3'
 )
