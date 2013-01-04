#!/usr/bin/env python

import argparse
import subprocess


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

    args = parser.parse_args()

    if args.stop_port is None:
        args.stop_port = int(args.port) + 1000

    print args

    pargs = [
        'java',
        '-jar',
        'usr/share/repose/repose-valve.jar',
        '-c', str(args.config_dir),
        '-p', str(args.port),
        '-s', str(args.stop_port)
    ]

    if args.insecure:
        pargs.append('-k')

    pargs.append('start')

    p1 = subprocess.Popen(pargs)
    p1.wait()

if __name__ == '__main__':
    run()
