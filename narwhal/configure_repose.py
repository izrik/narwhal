#!/usr/bin/env python

import argparse
from conf import (NamedConfigSetNotFoundException, process_config_set,
                  get_configs_folder, get_config_sets)


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
