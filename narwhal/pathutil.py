#!/usr/bin/env python

import os
import shutil

from . import __version__


def delete_folder(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)


def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def clear_folder(folder_name):
    for _name in os.listdir(folder_name):
        name = join(folder_name, _name)
        if os.path.isdir(name):
            delete_folder(name)
        else:
            os.remove(name)


def join(a, *p):
    return os.path.normpath(os.path.join(a, *p))
