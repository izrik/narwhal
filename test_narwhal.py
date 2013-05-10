#!/usr/bin/env python

from narwhal import conf
from narwhal import repose
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
        conf.process_folder_contents(folder='test-configs', dest_path='test/conf',
                                     params={'port': 12345})

    def tearDown(self):
        if self.valve is not None:
            logger.debug('shutting down valve')
            self.valve.stop()

    def test_wait_on_start(self):
        logger.debug('starting valve')
        self.valve = repose.ReposeValve(config_dir='test/conf', port=12345,
                                        stop_port=6789, wait_on_start=True,
                                        jar_file='test/bin/repose-valve.jar')
        logger.debug('valve started, checking port')
        resp = requests.get('http://localhost:12345/')
        self.assertEqual(resp.status_code, 200)
        logger.debug('good to go')


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
