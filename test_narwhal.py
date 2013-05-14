#!/usr/bin/env python

from narwhal import conf
from narwhal import valve
from narwhal import pathutil
from narwhal.download_repose import ReposeMavenConnector
import unittest2 as unittest
import requests
import os.path
import argparse
import logging


logger = logging.getLogger(__name__)


def setUpModule():
    pathutil.create_folder('test/bin')
    pathutil.create_folder('test/conf')
    pathutil.create_folder('test/log')
    pathutil.create_folder('test/var')
    #pathutil.clear_folder('test/bin')
    pathutil.clear_folder('test/conf')
    pathutil.clear_folder('test/log')
    pathutil.clear_folder('test/var')
    if not os.path.exists('test/bin/repose-valve.jar'):
        rmc = ReposeMavenConnector()
        logger.debug('Downloading valve jar')
        rmc.get_repose(valve_dest='test/bin/repose-valve.jar',
                       get_filter=False, get_ext_filter=False)
    if not os.path.exists('test/bin/filter-bundle.ear'):
        rmc = ReposeMavenConnector()
        logger.debug('Downloading filter bundle')
        rmc.get_repose(filter_dest='test/bin/filter-bundle.ear',
                       get_valve=False, get_ext_filter=False)
    logger.debug('module setup complete')


class TestValveWaitOnStart(unittest.TestCase):
    def setUp(self):
        self.valve = None
        logger.debug('Setting config files')
        conf.process_folder_contents(folder='test-configs',
                                     dest_path='test/conf',
                                     params={'port': 12345})

    def tearDown(self):
        if self.valve is not None:
            logger.debug('shutting down valve')
            self.valve.stop()

    def test_wait_on_start(self):
        logger.debug('starting valve')
        self.valve = valve.Valve(config_dir='test/conf', port=12345,
                                 stop_port=6789, wait_on_start=True,
                                 jar_file='test/bin/repose-valve.jar')
        logger.debug('valve started, checking port')
        resp = requests.get('http://localhost:12345/')
        self.assertEqual(resp.status_code, 200)
        logger.debug('good to go')


class TestValveArgs(unittest.TestCase):
    def test_config_dir(self):
        pargs = valve.Valve.construct_args(config_dir='asdf', port=None,
                                           https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=None, insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'asdf', 'start'])

        pargs = valve.Valve.construct_args(config_dir='path/to/configs',
                                           port=None, https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=None, insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'path/to/configs', 'start'])

        pargs = valve.Valve.construct_args(config_dir='path with spaces',
                                           port=None, https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=None, insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'path with spaces', 'start'])

    def test_port(self):
        pass

    def test_https_port(self):
        pass

    def test_jar_file(self):
        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=None, insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'conf', 'start'])

        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file='path/to/file.jar',
                                           stop_port=None, insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', 'path/to/file.jar',
                                 '-c', 'conf', 'start'])

        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file='filename with spaces.jar',
                                           stop_port=None, insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', 'filename with spaces.jar',
                                 '-c', 'conf', 'start'])

    def test_stop_port(self):
        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=None, insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'conf', 'start'])

        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=7777, insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'conf', '-s', '7777', 'start'])

        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port='8888', insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'conf', '-s', '8888', 'start'])

    def test_insecure(self):
        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=None, insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'conf', 'start'])

        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=None, insecure=True,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'conf', '-k', 'start'])

    def test_conn_fw(self):
        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=None, insecure=False,
                                           conn_fw=None)
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'conf', 'start'])

        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=None, insecure=False,
                                           conn_fw='jersey')
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'conf', '-cf', 'jersey', 'start'])

        pargs = valve.Valve.construct_args(config_dir='conf', port=None,
                                           https_port=None,
                                           jar_file=valve._default_jar_file,
                                           stop_port=None, insecure=False,
                                           conn_fw='apache')
        self.assertEqual(pargs, ['java', '-jar', valve._default_jar_file,
                                 '-c', 'conf', '-cf', 'apache', 'start'])


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--print-log', help="Print the log to STDERR.",
                        action='store_true')
    args = parser.parse_args()

    if args.print_log:
        logging.basicConfig(level=logging.DEBUG,
                            format=('%(asctime)s %(levelname)s:%(name)s:'
                                    '%(funcName)s:'
                                    '%(filename)s(%(lineno)d):'
                                    '%(threadName)s(%(thread)d):%(message)s'))

    unittest.main(argv=[''])


if __name__ == '__main__':
    run()
