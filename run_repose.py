#!/usr/bin/env python

import argparse
import time

import repose


def run():

    parser = argparse.ArgumentParser()
    parser.add_argument('config_dir',
                        help='The location of the Repose config directory.')
    parser.add_argument('port', type=int,
                        help='The port on which Repose will listen for '
                        'requests.')
    parser.add_argument('--stop-port', type=int, default=None,
                        help='The port on which Repose will listen for the '
                        'shutdown command. Default is PORT+1000.')
    parser.add_argument('--insecure', help='Don\'t verify SSL certs.',
                        action='store_true')
    parser.add_argument('--jar-file', help='The Repose Valve JAR file to run.',
                        default=repose._default_jar_file)

    args = parser.parse_args()

    if args.stop_port is None:
        args.stop_port = int(args.port) + 1000

    r = repose.ReposeValve(jar_file=args.jar_file, config_dir=args.config_dir,
                           port=args.port, stop_port=args.stop_port,
                           insecure=args.insecure)

    time.sleep(35)

    r.stop()


if __name__ == '__main__':
    run()
