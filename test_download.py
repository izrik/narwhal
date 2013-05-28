#!/usr/bin/env python

from narwhal.rmaven import ReposeMavenConnector as RMC
import unittest
import argparse
import logging
import os


logger = logging.getLogger(__name__)


class TestInitialization(unittest.TestCase):
    def test_init_no_param(self):
        rmc = RMC()
        self.assertEqual(rmc.root,
                         'maven.research.rackspacecloud.com/'
                         'content/repositories')

    def test_init_with_root(self):
        rmc = RMC('some-value')
        self.assertEqual(rmc.root, 'some-value')


class TestCommandLine(unittest.TestCase):
    def setUp(self):
        os.system('rm -rf usr')

    def test_download_valve(self):
        os.system('narwhal/download_repose.py --no-filter --no-ext-filter')
        self.assertTrue(os.path.exists('usr/share/repose/repose-valve.jar'))

    def test_download_filter(self):
        os.system('narwhal/download_repose.py --no-valve --no-ext-filter')
        self.assertTrue(os.path.exists('usr/share/repose/filters/'
                                       'filter-bundle.ear'))

    def test_download_ext_valve(self):
        os.system('narwhal/download_repose.py --no-filter --no-valve')
        self.assertTrue(os.path.exists('usr/share/repose/filters/'
                                       'extensions-filter-bundle.ear'))

    def tearDown(self):
        os.system('rm -rf usr')


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--print-log', action='store_true',
                        help='Print the log.')
    args = parser.parse_args()

    if args.print_log:
        logging.basicConfig(level=logging.DEBUG,
                            format=('%(asctime)s %(levelname)s:%(name)s:'
                                    '%(funcName)s:'
                                    '%(filename)s(%(lineno)d):'
                                    '%(threadName)s(%(thread)d):%(message)s'))

    #rmc = ReposeMavenConnector()

    #x = rmc.get_repose()

    #y = rmc.get_repose(snapshot=True)

    #z = rmc.get_repose(version='2.5.0', get_ext_filter=False,
    #                   get_filter=False)
    #w = rmc.get_repose(snapshot=True, version='2.5.1', get_ext_filter=False,
    #                   get_filter=False)

    #test_runner = xmlrunner.XMLTestRunner(output='test-reports')

    #unittest.main(argv=[''], testRunner=test_runner)
    unittest.main(argv=[''])

if __name__ == '__main__':
    run()
