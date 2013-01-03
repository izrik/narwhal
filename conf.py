#!/usr/bin/env python

import argparse
import inspect
import os
import string
import xml.etree.ElementTree as et


def get_config_sets(configs_folder):
    for entry in os.listdir(configs_folder):
        # TODO: os.path.join
        if os.path.isdir('%s/%s' % (configs_folder, entry)):
            if os.path.exists('%s/%s/%s' % (configs_folder, entry, '.config-set.xml')):
                yield entry


def copy_and_apply_params(source, dest, params={}):
    with open(source, 'r') as input:
        template = string.Template(input.read())

    with open(dest, 'w') as output:
        subst = template.safe_substitute(params)
        # TODO: Warn of un-substituted parameters
        output.write(subst)


def process_config_set(config_set_name, configs_folder, params={}):
    # TODO: os.path.join
    config_xml = et.parse('%s/%s/.config-set.xml' % (configs_folder, config_set_name))
    for folder in config_xml.findall('folder'):
        folder_path = folder.attrib.get('path', '.')
        for f in folder.findall('file'):
            file_source = os.path.join(configs_folder, config_set_name, f.attrib['src'])
            file_basename = os.path.basename(file_source)
            file_dest = os.path.join(folder_path, file_basename)
            applying = ''
            if len(params) > 0:
                applying = ', applying config parameters' # TODO: maybe output parameters provided/substituted?

            print 'Copy from "%s" to "%s"%s' % (file_source, file_dest, applying)
            copy_and_apply_params(file_source, file_dest, params)


def run():
    _script_filename = os.path.abspath(inspect.getfile(inspect.currentframe()))
    _script_folder = os.path.dirname(_script_filename)

    parser = argparse.ArgumentParser(description='Copy config files', version='1.0')
    parser.add_argument('--param', action='append', help='A name/value pair for substitution of template parameters.')
    parser.add_argument(metavar='config-set', nargs='+', dest='config_sets', help='A set of configuration files to copy. Must be a named config set in the configs/ folder.')
    args = parser.parse_args()

    params = {}
    for param in args.param:
        name, value = param.split('=', 2)
        params[name] = value
    args.params = params

    # TODO: os.path.join
    configs_folder = '%s/configs' % _script_folder
    available_config_sets = [cs for cs in get_config_sets(configs_folder)]

    requested_config_sets = args.config_sets

    error = False

    for cs in requested_config_sets:
        if cs not in available_config_sets:
            print 'Error: no config set named %s' % cs
            error = True

    if error:
        print 'Available config sets:'
        for cs in available_config_sets:
            print '  %s' % cs

    for cs in requested_config_sets:
        process_config_set(cs, configs_folder, params)


if __name__ == '__main__':
    run()
