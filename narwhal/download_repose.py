#!/usr/bin/env python

import argparse
import logging
import rmaven

from . import __version__


logger = logging.getLogger(__name__)

_default_valve_dest = 'usr/share/repose/repose-valve.jar'
_default_filter_dest = 'usr/share/repose/filters/filter-bundle.ear'
_default_ext_filter_dest = ('usr/share/repose/filters/'
                            'extensions-filter-bundle.ear')

objects = [
    {
        'name': 'valve',
        'path': 'com/rackspace/papi/core/valve',
        'extension': 'jar'
    },
    {
        'name': 'filter',
        'path': 'com/rackspace/papi/components/filter-bundle',
        'extension': 'ear'
    },
    {
        'name': 'ext-filter',
        'path': 'com/rackspace/papi/components/extensions/'
                'extensions-filter-bundle',
        'extension': 'ear'
    },
]

objects_by_name = dict(((obj['name'], obj) for obj in objects))


def get_repose_object_url(rmc, obj, snapshot=False, version=None):
    return rmc.get_repose_artifact_url(path=obj['path'],
                                       extension=obj['extension'],
                                       snapshot=snapshot, version=version)


def get_repose_valve_url(rmc, snapshot=False, version=None):
    return get_repose_object_url(rmc, objects_by_name['valve'],
                                 snapshot=snapshot, version=version)


def get_filter_bundle_url(rmc, snapshot=False, version=None):
    return get_repose_object_url(rmc, objects_by_name['filter'],
                                 snapshot=snapshot, version=version)


def get_extensions_filter_bundle_url(rmc, snapshot=False, version=None):
    return get_repose_object_url(rmc, objects_by_name['ext-filter'],
                                 snapshot=snapshot, version=version)


def get_repose(rmc, valve_dest=None, filter_dest=None,
               ext_filter_dest=None, get_valve=True, get_filter=True,
               get_ext_filter=True, snapshot=False, version=None):

    if valve_dest is None:
        valve_dest = _default_valve_dest
    if filter_dest is None:
        filter_dest = _default_filter_dest
    if ext_filter_dest is None:
        ext_filter_dest = _default_ext_filter_dest

    if get_valve:
        vurl = get_repose_valve_url(rmc, snapshot=snapshot, version=version)
    if get_filter:
        furl = get_filter_bundle_url(rmc, snapshot=snapshot, version=version)
    if get_ext_filter:
        eurl = get_extensions_filter_bundle_url(rmc, snapshot=snapshot,
                                                version=version)

    filenames = {}

    if get_valve:
        valve_dest = rmc.clean_up_dest(vurl, valve_dest)
        print '%s --> %s' % (vurl, valve_dest)
        if vurl:
            rmc.download_file(url=vurl, dest=valve_dest)
            filenames["valve"] = valve_dest

    if get_filter:
        filter_dest = rmc.clean_up_dest(furl, filter_dest)
        print '%s --> %s' % (furl, filter_dest)
        if furl:
            rmc.download_file(url=furl, dest=filter_dest)
            filenames["filter"] = filter_dest

    if get_ext_filter:
        ext_filter_dest = rmc.clean_up_dest(eurl, ext_filter_dest)
        print '%s --> %s' % (eurl, ext_filter_dest)
        if eurl:
            rmc.download_file(url=eurl, dest=ext_filter_dest)
            filenames["ext_filter"] = ext_filter_dest

    return filenames


def run():

    parser = argparse.ArgumentParser()
    parser.add_argument('--valve-dest', help='The name that the Valve JAR '
                        'should be renamed to, or the directory where it '
                        'should be downloaded to.')
    parser.add_argument('--filter-dest', help='The name that the filter '
                        'bundle EAR file should be renamed to, or the '
                        'directory where it should be downloaded to.')
    parser.add_argument('--ext-filter-dest', help='The name that the '
                        'extension filter bundle EAR file should be renamed '
                        'to, or the directory where it should be downloaded '
                        'to.')
    parser.add_argument('--no-valve',
                        help='Don\'t download the valve JAR file',
                        action='store_true')
    parser.add_argument('--no-filter', help='Don\'t download the standard '
                        'filter bundle EAR file', action='store_true')
    parser.add_argument('--no-ext-filter', help='Don\'t download the '
                        'extension filter bundle EAR file',
                        action='store_true')
    parser.add_argument('--url-root', help='The url (with path) to download '
                        'artifacts from.')
    parser.add_argument('--snapshot', help='Download a SNAPSHOT build instead '
                        'of a release build.', action='store_true')
    parser.add_argument('--version', help='The version of the artifacts to '
                        'download. Typically of the forms "x.y.z" for '
                        'releases, "x.y.z-SNAPSHOT" for the most recent '
                        'snapshot build in version x.y.z, and '
                        '"x.y.z-date.time-build" for a specific snapshot '
                        'build.', type=str)
    parser.add_argument('--print-log', help="Print the log to STDERR.",
                        action='store_true')
    parser.add_argument('--full-log', help="Log more information.",
                        action='store_true')
    args = parser.parse_args()

    if args.print_log:
        if args.full_log:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(levelname)s:%(name)s:%(funcName)s:'
                                '%(filename)s(%(lineno)d):%(threadName)s'
                                '(%(thread)d):%(message)s')
        else:
            logging.basicConfig(level=logging.DEBUG)

    rmc = rmaven.ReposeMavenConnector(args.url_root)
    get_repose(rmc, valve_dest=args.valve_dest, filter_dest=args.filter_dest,
               ext_filter_dest=args.ext_filter_dest,
               get_valve=not args.no_valve, get_filter=not args.no_filter,
               version=args.version, get_ext_filter=not args.no_ext_filter,
               snapshot=args.snapshot)


if __name__ == '__main__':
    run()
