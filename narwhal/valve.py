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


class Valve:
    def __init__(self, config_dir, port=None, https_port=None, jar_file=None,
                 stop_port=None, insecure=False, wait_on_start=False,
                 wait_timeout=None, conn_fw=None):
        logger.debug('Creating new Valve object (config_dir=%s, '
                     'jar_file=%s, stop_port=%s, insecure=%s)' %
                     (config_dir, jar_file, stop_port, insecure))

        if jar_file is None:
            jar_file = _default_jar_file

        if stop_port is None:
            if port is None:
                stop_port = 9090
            else:
                stop_port = port + 1000

        if wait_on_start and port is None and https_port is None:
            raise ValueError("Either 'port' and/or 'https_port' must specify "
                             "a port number if 'wait_on_start' is True")

        if conn_fw is not None:
            fws = ['jersey', 'apache']
            if conn_fw not in fws:
                raise ValueError('"%s" is not a valid connection framework. '
                                 'If sepecified, conn_fw must be one of: '
                                 '[%s]' % conn_fw, ', '.join(fws))

        pargs = self.construct_args(config_dir=config_dir, port=port,
                                    https_port=https_port, jar_file=jar_file,
                                    stop_port=stop_port, insecure=insecure,
                                    conn_fw=conn_fw)

        self.config_dir = config_dir
        self.port = port
        self.https_port = https_port
        self.jar_file = jar_file
        self.stop_port = stop_port
        self.insecure = insecure

        logger.debug('Starting valve with the following command line: "%s"' %
                     ' '.join(pargs))

        self.proc = subprocess.Popen(pargs, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
        self.stdout = ThreadedStreamReader(self.proc.stdout)
        self.stderr = ThreadedStreamReader(self.proc.stderr)

        if wait_on_start:
            self.wait_for_node_to_start(wait_timeout=wait_timeout)

        logger.debug('New Valve object initialized (pid=%i)' %
                     self.proc.pid)

    @staticmethod
    def construct_args(config_dir, port, https_port, jar_file, stop_port,
                       insecure, conn_fw):
        """Take the provided parameters and turn them into the command line
        arguments to invoke Valve."""

        pargs = [
            'java', '-jar', jar_file,
            '-c', config_dir,
        ]

        if stop_port is not None:
            pargs.append('-s')
            pargs.append(str(stop_port))

        if port is not None:
            pargs.append('-p')
            pargs.append(str(port))

        if https_port is not None:
            pargs.append('-ps')
            pargs.append(str(https_port))

        if insecure:
            pargs.append('-k')

        if conn_fw is not None:
            pargs.append('-cf')
            pargs.append(conn_fw)

        pargs.append('start')

        return pargs

    def wait_for_node_to_start(self, wait_timeout=None):
        if self.port is None and self.https_port is None:
            raise ValueError("No valid port was set. Cannot wait on the node.")

        if self.port is not None:
            wait_url = 'http://localhost:%s/' % str(self.port)
        else:
            wait_url = 'https://localhost:%s' % str(self.https_port)

        wait_for_node_to_start(url=wait_url, wait_timeout=wait_timeout)

    def stop(self, wait=True):
        try:
            logger.debug('Shutting down stdout and stderr readers.')
            self.stdout.shutdown()
            self.stderr.shutdown()

            logger.debug('Attempting to stop Valve object (pid=%i, '
                         'stop_port=%s)' % (self.proc.pid, self.stop_port))
            s = socket.create_connection(('localhost', self.stop_port))
            s.send('stop\r\n')
            if wait:
                logger.debug('Waiting for process to end (pid=%i)' %
                             self.proc.pid)
                self.wait(timeout=30)
                if self.proc.poll() is None:
                    # it timed out while waiting
                    raise Exception
        except:
            logger.debug('Couldn\'t stop using the stop port, killing instead '
                         '(pid=%i)' % self.proc.pid)
            self.proc.kill()
        logger.debug('Valve stopped (pid=%i)' % self.proc.pid)

    def wait(self, timeout=30):
        t1 = time.time()
        while True:
            logger.debug('polling')
            if self.proc.poll() is not None:
                logger.debug('child process stopped')
                return
            t2 = time.time()
            if timeout is not None and t2 - t1 > timeout:
                logger.debug('timed out')
                return
            time.sleep(1)


def wait_for_node_to_start(url=None, scheme='http', port=None,
                           wait_timeout=None):
    if url is None:
        if port is None:
            raise ArgumentError("Must specify either url or port "
                                "parameter.")
        url = '%s://localhost:%s' % (scheme, port)

    t1 = time.time()
    while True:
        try:
            resp = requests.get(url)
            if int(resp.status_code) != 500:
                # if it's not a 500 error, then it's done starting
                break
        except:
            pass
        time.sleep(1)
        t2 = time.time()
        if wait_timeout is not None and t2 - t1 > wait_timeout:
            logger.debug('wait_on_start timed out')
            break


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
