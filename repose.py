#!/usr/bin/env python

import subprocess
import socket


_default_jar_file = 'usr/share/repose/repose-valve.jar'


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
        self.stdout = self.proc.stdout
        self.stderr = self.proc.stderr

    def stop(self, wait=True):
        s = socket.create_connection(('localhost', self.stop_port))
        s.send('stop\r\n')
        if wait:
            self.wait()

    def wait(self):
        return self.proc.communicate()
