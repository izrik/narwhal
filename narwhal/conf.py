#!/usr/bin/env python

import argparse
import inspect
import os
import string
import xml.etree.ElementTree as et
import pathutil

from . import __version__


def get_configs_folder():
    _script_filename = os.path.abspath(inspect.getfile(inspect.currentframe()))
    _script_folder = os.path.dirname(_script_filename)
    configs_folder = '%s/configs' % _script_folder
    return configs_folder


def get_config_sets(configs_folder):
    if not os.path.exists(configs_folder) or not os.path.isdir(configs_folder):
        return
    for entry in os.listdir(configs_folder):
        if os.path.isdir('%s/%s' % (configs_folder, entry)):
            if os.path.exists(pathutil.join(configs_folder, entry,
                                            '.config-set.xml')):
                yield entry


def process_config_set(config_set_name, destination_path=None,
                       configs_folder=None, params=None, verbose=True):

    if params is None:
        params = {}

    if os.path.isfile(config_set_name):
        # it's a file
        config_xml = et.parse(config_set_name)
        source_context = os.path.dirname(config_set_name)
    else:
        # try a named config set in the configs folder
        if configs_folder is None:
            configs_folder = get_configs_folder()
        if config_set_name not in get_config_sets(configs_folder):
            raise NamedConfigSetNotFoundException(config_set_name)
        filename = pathutil.join(configs_folder, config_set_name,
                                 '.config-set.xml')
        config_xml = et.parse(filename)
        source_context = pathutil.join(configs_folder, config_set_name)

    for folder in config_xml.findall('folder'):
        folder_path = folder.attrib.get('path', '.')
        for f in folder.findall('file'):
            file_source = pathutil.join(source_context, f.attrib['src'])
            file_basename = os.path.basename(file_source)
            if destination_path and folder_path:
                full_dest = pathutil.join(destination_path, folder_path)
            elif destination_path:
                full_dest = destination_path
            elif folder_path:
                full_dest = folder_path
            else:
                full_dest = '.'
            pathutil.create_folder(full_dest)
            file_dest = pathutil.join(full_dest, file_basename)

            if verbose:
                applying = ''
                if len(params) > 0:
                    # TODO: maybe output parameters provided/substituted?
                    applying = ', applying config parameters'

                print ('Copy from "%s" to "%s"%s' %
                       (file_source, file_dest, applying))

            copy_and_apply_params(file_source, file_dest, params, verbose)


class NamedConfigSetNotFoundException(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "No config set named \"%s\" was found." % self.name


def copy_and_apply_params(source, dest, params={}, verbose=True):
    with open(source, 'r') as input:
        template = string.Template(input.read())

    with open(dest, 'w') as output:
        subst = template.safe_substitute(params)
        unsubst = template.pattern.findall(subst)
        if verbose:
            for match in unsubst:
                name = match[1] or match[2] or None
                if name is not None:
                    print ("Warning: Unsubstituted value \"%s\" in template." %
                           name)
        output.write(subst)


def run():
    parser = argparse.ArgumentParser(description='Copy config files',
                                     version='1.0')
    parser.add_argument('--param', action='append',
                        help='A name/value pair for substitution of template '
                        'parameters.')
    parser.add_argument(metavar='config-set', dest='config_set',
                        help='A set of configuration files to copy. Must be a '
                        'named config set in the configs/ folder.')
    parser.add_argument('--dest-path', dest='dest_path',
                        help='Where to put the files.')
    args = parser.parse_args()

    params = {}
    if args.param is not None:
        for param in args.param:
            parts = param.split('=', 2)
            if len(parts) > 1:
                name, value = parts
            else:
                name, value = parts[0], 'true'
            params[name] = value
    args.params = params

    configs_folder = get_configs_folder()

    config_set = args.config_set
    dest_path = args.dest_path

    try:
        process_config_set(config_set_name=config_set,
                           configs_folder=configs_folder, params=params,
                           destination_path=dest_path)

    except NamedConfigSetNotFoundException as e:
        print 'Error: %s' % str(e)
        found = False
        for cs in get_config_sets(configs_folder):
            if not found:
                print 'Available config sets:'
            print '  %s' % cs
            found = True
        if not found:
            print 'No available config sets found'


if __name__ == '__main__':
    run()
