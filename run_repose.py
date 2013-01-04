#!/usr/bin/env python

import argparse
import subprocess
import time
import socket

_default_jar_file = 'usr/share/repose/repose-valve.jar'


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
                        default=_default_jar_file)

    args = parser.parse_args()

    if args.stop_port is None:
        args.stop_port = int(args.port) + 1000

    r = ReposeValve(jar_file=args.jar_file, config_dir=args.config_dir,
                    port=args.port, stop_port=args.stop_port,
                    insecure=args.insecure)

    time.sleep(35)

    r.stop()


class ReposeValve:
    def __init__(self, config_dir, port, jar_file=None, stop_port=None,
                 insecure=False):

        if jar_file is None:
            jar_file = _default_jar_file

        if stop_port is None:
            stop_port = port + 1000

        self.config_dir = config_dir
        self.port = port
        self.jar_file = jar_file
        self.stop_port = stop_port
        self.insecure = insecure

        pargs = [
            'java', '-jar', jar_file,
            '-c', config_dir,
            '-p', str(port),
            '-s', str(stop_port)
        ]

        if insecure:
            pargs.append('-k')

        pargs.append('start')

        self.proc = subprocess.Popen(pargs, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)

    def stop(self):
        s = socket.create_connection(('localhost', self.stop_port))
        s.send('stop\r\n')
        if self.proc.poll() is None:
            self.proc.communicate()


if __name__ == '__main__':
    run()
