#!/usr/bin/env python

# Copyright (C) 2012-2013 Richard Sartor <richard.sartor@rackspace.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import subprocess
import socket
import logging
import threading
import Queue
import time
import requests

from . import __version__


logger = logging.getLogger(__name__)


_default_jar_file = 'usr/share/repose/repose-valve.jar'


class ReposeValve:
    def __init__(self, config_dir, port=None, https_port=None, jar_file=None,
                 stop_port=None, insecure=False, wait_on_start=False):
        logger.debug('Creating new ReposeValve object (config_dir=%s, '
                     'jar_file=%s, stop_port=%s, insecure=%s)' %
                     (config_dir, jar_file, stop_port, insecure))

        if jar_file is None:
            jar_file = _default_jar_file

        if stop_port is None:
            if port is None:
                stop_port = 9090
            else:
                stop_port = port + 1000

        if wait_on_start:
            if port is not None:
                wait_url = 'http://localhost:%s/' % str(port)
            elif https_port is not None:
                wait_url = 'https://localhost:%s' % str(https_port)
            else:
                raise ValueError("Either 'port' and/or 'https_port' must "
                                 "specify a port number if 'wait_on_start' is "
                                 "True")

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

        if https_port is not None:
            pargs.append('-ps')
            pargs.append(str(https_port))

        if insecure:
            pargs.append('-k')

        pargs.append('start')

        logger.debug('Starting valve with the following command line: "%s"' %
                     ' '.join(pargs))

        self.proc = subprocess.Popen(pargs, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        self.stdout = ThreadedStreamReader(self.proc.stdout)
        self.stderr = ThreadedStreamReader(self.proc.stderr)

        if wait_on_start:
            wait_count = 0
            while True:
                try:
                    sc = requests.get(wait_url)
                    if int(sc) == 200:
                        break
                except:
                    pass
                time.sleep(1)
                wait_count += 1
                if wait_count > 30:
                    break

        logger.debug('New ReposeValve object initialized (pid=%i)' %
                     self.proc.pid)

    def stop(self, wait=True):
        try:
            logger.debug('Shutting down stdout and stderr readers.')
            self.stdout.shutdown()
            self.stderr.shutdown()

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


class ThreadedStreamReader:
    def __init__(self, stream):
        self.stream = stream
        self.queue = Queue.Queue()
        self._shutdown = False
        self.thread = threading.Thread(target=self._thread_target)
        self.thread.daemon = True
        self.thread.start()

    def _thread_target(self):
        for line in self.stream.xreadlines():
            if self._shutdown:
                break
            self.queue.put(line)

    def readline(self, timeout=None):
        s = self.queue.get(timeout=timeout)
        self.queue.task_done()
        return s

    def readlines(self):
        lines = []
        while not self.queue.empty():
            lines.append(self.readline())
        return lines

    def shutdown(self):
        self._shutdown = True


def stream_printer(fin, fout):
    while True:
        for line in fin.readlines():
            fout.write(line)
            fout.flush()
        time.sleep(1)
