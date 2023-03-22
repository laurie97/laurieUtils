"""
Functions to connect and manipulate django stuff
"""

import os
import django
import sys

def find_dir_path(name, path):
    """
    Find the path of a directory that contains a directory inside of a given path.

    i.e. if dir 'ifa_standards_rms' is at path 'lmcclymont/ids/ifa_standards_rms'
    return 'lmcclymont/ids'

    Returns the first instance found using os.walk

    Args:
    - name: str, name of dir to find
    - path: str, path to find dir within

    Returns:
    - root: str, path of directory that has been found
    """
    for root, dirs, files in os.walk(path):
        if name in dirs:
            return root


### Set Up Django

def connect_to_ids_django(ids_path=None):
    """
    Connect to IDS django database to enable querying from jupyter notebook
    Based on https://www.youtube.com/watch?v=t3mk_u0rprM.

    Uses os.chdir, but hopefully smart enough to always return you to your working dir after.
    Based on : https://stackoverflow.com/questions/41577392/how-to-kill-os-chdir-and-use-the-further-code

    Args:
    - ids_path: str, path to the ids project. If none I will try and find it for you

    Exceptions:
    - Will throw an exception if django.setup() fails, whihc normally means
    """

    current_path = os.getcwd()
 
    ## If path to ids isn't set up then I will try and find it, this takes ~15-30 seconds
    if not ids_path:
        userhome = os.path.expanduser("~")
        ids_path = find_dir_path('ifa_standards_rms', userhome)
        
    ## Connect to IDS Django and set-up environment
    try:
        sys.path.append(ids_path)
        os.chdir(ids_path)
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ifa_standards_rms.settings.local")
        django.setup()

    ## Any failure and give the error statement   
    except:
        error_statement=(
        f'''Couldn't run django.setup() 
        Perhaps it couldn't find Django Module!!
        - Have you started the server?
        - Is your ids folder found at: {ids_path}
        ''')
        raise ModuleNotFoundError(error_statement)

    ## Finnaly, always change dir back to current path
    finally:
        os.chdir(current_path)