#!/usr/bin/env python

import argparse
import logging
import rmaven

from . import __version__


logger = logging.getLogger(__name__)


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
    rmc.get_repose(valve_dest=args.valve_dest,
                   filter_dest=args.filter_dest,
                   ext_filter_dest=args.ext_filter_dest,
                   get_valve=not args.no_valve, get_filter=not args.no_filter,
                   version=args.version, get_ext_filter=not args.no_ext_filter,
                   snapshot=args.snapshot)


if __name__ == '__main__':
    run()
