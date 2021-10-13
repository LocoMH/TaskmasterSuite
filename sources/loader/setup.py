from distutils.core import setup
import py2exe
import sys
import os

sys.argv.append('py2exe')

setup(
    options={'py2exe': {'bundle_files': 1,
                        'compressed': True, }},
    windows=[
        {
            'script': "loader.py",
            "icon_resources": [(1, "../frontend/tm.ico")],
            "dest_base": "loader"
        }
    ],
    zipfile=None,
)
