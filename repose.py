#!/usr/bin/env python

import subprocess
import socket
import logging
import threading


logger = logging.getLogger(__name__)


_default_jar_file = 'usr/share/repose/repose-valve.jar'


class ThreadedStreamReader:
    def __init__(self, stream):
        self.stream = stream
        self.thread = threading.Thread(target=self.thread_target)
        self.thread.daemon = True
        self.thread.start()

    def thread_target(self):
        pass

    def readline(self):
        pass

    def readlines(self):
        pass


class ReposeValve:
    def __init__(self, config_dir, port=None, jar_file=None, stop_port=None,
                 insecure=False):
        logger.debug('Creating new ReposeValve object (config_dir=%s, '
                     'jar_file=%s, stop_port=%s, insecure=%s)' %
                     (config_dir, jar_file, stop_port, insecure))

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
            '-s', str(stop_port)
        ]

        if port is not None:
            pargs.append('-p')
            pargs.append(str(port))

        if insecure:
            pargs.append('-k')

        pargs.append('start')

        self.proc = subprocess.Popen(pargs, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        self.stdout = ThreadedStreamReader(self.proc.stdout)
        self.stderr = ThreadedStreamReader(self.proc.stderr)
        logger.debug('New ReposeValve object initialized (pid=%i)' %
                     self.proc.pid)

    def stop(self, wait=True):
        try:
            logger.debug('Attempting to stop ReposeValve object (pid=%i, '
                         'stop_port=%s)' % (self.proc.pid, self.stop_port))
            s = socket.create_connection(('localhost', self.stop_port))
            s.send('stop\r\n')
            if wait:
                logger.debug('Waiting for process to end (pid=%i)' %
                             self.proc.pid)
                self.wait()
        except:
            logger.debug('Couldn\'t stop using the stop port, killing instead '
                         '(pid=%i)' % self.proc.pid)
            self.proc.kill()
        logger.debug('Repose stopped (pid=%i)' % self.proc.pid)

    def wait(self):
        return self.proc.communicate()
