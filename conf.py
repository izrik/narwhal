#!/usr/bin/env python

import argparse
import inspect
import os
import string
import xml.etree.ElementTree as et


def get_configs_folder():
    _script_filename = os.path.abspath(inspect.getfile(inspect.currentframe()))
    _script_folder = os.path.dirname(_script_filename)
    configs_folder = '%s/configs' % _script_folder
    return configs_folder


def get_config_sets(configs_folder):
    for entry in os.listdir(configs_folder):
        # TODO: os.path.join
        if os.path.isdir('%s/%s' % (configs_folder, entry)):
            if os.path.exists('%s/%s/%s' %
                              (configs_folder, entry, '.config-set.xml')):
                yield entry


def process_config_set(config_set_name, configs_folder=None, params=None, verbose=True):
    if configs_folder is None:
        configs_folder = get_configs_folder()

    if params is None:
        params = {}

    if config_set_name not in get_config_sets(configs_folder):
        raise NamedConfigSetNotFoundException(cs)

    # TODO: os.path.join
    config_xml = et.parse('%s/%s/.config-set.xml' %
                          (configs_folder, config_set_name))
    for folder in config_xml.findall('folder'):
        folder_path = folder.attrib.get('path', '.')
        for f in folder.findall('file'):
            file_source = os.path.join(configs_folder, config_set_name,
                                       f.attrib['src'])
            file_basename = os.path.basename(file_source)
            file_dest = os.path.join(folder_path, file_basename)

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
                    print "Warning: Unsubstituted value \"%s\" in template." % name
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

    # TODO: os.path.join
    configs_folder = get_configs_folder()

    config_set = args.config_set

    try:
        process_config_set(config_set, configs_folder, params)

    except NamedConfigSetNotFoundException as e:
        print 'Error: %s' % str(e)
        print 'Available config sets:'
        for cs in get_config_sets(configs_folder):
            print '  %s' % cs


if __name__ == '__main__':
    run()
