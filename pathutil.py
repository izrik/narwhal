#!/usr/bin/env python

import os
import shutil


def delete_folder(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)


def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def join(a, *p):
    return os.path.normpath(os.path.join(a, *p))