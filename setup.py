from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='distorrent-python',
    version='1.0.0',
    description='''A broadcatcher with a web interface''',
    url='https://github.com/legbt/Distorrent-Python',
    author='LeGBT',
    author_email='cauchyunderground@gmail.com',
    license='GPLv3',
    classifiers=[
        #  1 - Planning
        #  2 - Pre-Alpha
        #  3 - Alpha
        #  4 - Beta
        #  5 - Production/Stable
        #  6 - Mature
        #  7 - Inactive
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Topic :: Broadcatch',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='torrent rss',
    py_modules=["app"],
    install_requires=["bottle", "requests", "untangle"],
    extras_require={},
    package_data={},
    data_files=[],
    entry_points={},
)
