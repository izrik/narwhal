#!/usr/bin/env python

import re
import logging
import requests
import xml.etree.ElementTree as et
import os
import sys

from . import __version__


logger = logging.getLogger(__name__)


class MavenConnector(object):
    def get_artifact_url(self, root, extension, snapshot=False, version=None):

        meta = '%s/maven-metadata.xml' % root
        metas = requests.get(meta).text
        metax = et.fromstring(metas)
        artifact_id = metax.find('artifactId').text
        if snapshot:
            if version is None:
                version = metax.find('versioning/latest').text
                m = re.match('(\d+\.\d+\.\d+)-SNAPSHOT', version)
                main_version = m.group(1)
                snapshot_version = None
            else:
                version = str(version)
                m = re.match('(\d+\.\d+\.\d+)(-SNAPSHOT|$)', version)
                if m is not None:
                    main_version = m.group(1)
                    snapshot_version = None
                else:
                    m = re.match('(\d+\.\d+\.\d+)-(\d+\.\d+-\d+)', version)
                    if m is None:
                        raise Exception('Invalid version format: "%s"' %
                                        version)
                    main_version = m.group(1)
                    snapshot_version = '%s-%s' % (main_version, m.group(2))
                found = False
                for vv in metax.findall('versioning/versions/version'):
                    # kludge - searching through the list because ET doesn't
                    # have complete xpath predicate support
                    if vv.text == '%s-SNAPSHOT' % main_version:
                        found = True
                        break
                if not found:
                    raise Exception('Version "%s" not found in the metadata' %
                                    main_version)
            version_root = '%s/%s-SNAPSHOT' % (root, main_version)
            meta2 = '%s/maven-metadata.xml' % version_root
            meta2s = requests.get(meta2).text
            meta2x = et.fromstring(meta2s)
            if snapshot_version is None:
                last_updated = meta2x.find('versioning/lastUpdated').text
                for elem in meta2x.findall('versioning/snapshotVersions/'
                                           'snapshotVersion'):
                    if (elem.find('extension').text == extension and
                            (not elem.find('classifier') or
                             elem.find('classifier').text != 'sources') and
                            elem.find('updated').text == last_updated):
                        snapshot_version = elem.find('value').text
            else:
                found = False
                for elem in meta2x.findall('versioning/snapshotVersions/'
                                           'snapshotVersion'):
                    if (elem.find('extension').text == extension and
                            elem.find('value').text == snapshot_version):
                        found = True
                if not found:
                    raise Exception('Snapshot version "%s" not found in the '
                                    'metadata' % (snapshot_version))
            artifact_url = '%s/%s-%s.%s' % (version_root, artifact_id,
                                            snapshot_version, extension)
            return artifact_url
        else:
            if version is None:
                version = metax.find('versioning/release').text
            else:
                version = str(version)
                found = False
                for vv in metax.findall('versioning/versions/version'):
                    # kludge - searching through the list because ET doesn't
                    # have complete xpath predicate support
                    if vv.text == version:
                        found = True
                        break
                if not found:
                    raise Exception('Version "%s" not found in the metadata' %
                                    version)
            version_root = '%s/%s' % (root, version)
            artifact_url = '%s/%s-%s.%s' % (version_root, artifact_id, version,
                                            extension)
            return artifact_url

        return None

    def clean_up_dest(self, url, dest=None):
        """Clean up the destination. If dest is None, use the filename of the
        file being downloaded and store it in the current directory. If dest
        ends with a '/', or if it points to a directory, use the filename of
        the file being downloaded and store it in the specified directory. If
        dest doesn't end with a '/' and doesn't point to a directory, store
        the file using the specfied filename. If the specified already exists,
        append a number to it."""
        if dest == '' or dest is None:
            dest = os.path.basename(url)
        else:
            logger.debug('cleaning up dest')
            logger.debug('dest: %s' % dest)
            logger.debug('os.path.isdir(dest): %s' % os.path.isdir(dest))
            basename = os.path.basename(dest)
            dirname = os.path.dirname(dest)
            if os.path.isdir(dest) or basename == '':
                basename = os.path.basename(url)
                dirname = dest
            else:
                basename = os.path.basename(dest)
                dirname = os.path.dirname(dest)
            logger.debug('basename: %s' % basename)
            logger.debug('dirname: %s' % dirname)
            basename = os.path.normpath(basename)
            dirname = os.path.normpath(dirname)
            logger.debug('basename: %s' % basename)
            logger.debug('dirname: %s' % dirname)
            logger.debug('os.path.exists(dirname): %s' %
                         str(os.path.exists(dirname)))
            if dirname != '' and os.path.exists(dirname):
                n = 1
                basename2 = basename
                logger.debug('basename2: %s' % basename2)
                logger.debug('os.path.exists(join(dirname, basename2)): %s'
                             % os.path.exists(os.path.join(dirname,
                                                           basename2)))
                while os.path.exists(os.path.join(dirname, basename2)):
                    basename2 = basename + '.%i' % n
                    n += 1
                    logger.debug('basename2: %s' % basename2)
                    logger.debug('os.path.exists(os.path.join(dirname, '
                                 'basename2)): %s' %
                                 os.path.exists(os.path.join(dirname,
                                                             basename2)))
                basename = basename2
            dest = os.path.join(dirname, basename)
            logger.debug('dest [final]: %s' % dest)
        return dest

    def download_file(self, url, dest):

        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise ValueError

        dirname = os.path.dirname(dest)
        if dirname != '' and not os.path.exists(dirname):
            os.makedirs(dirname)

        blocksize = 4096
        count = 0
        with open(dest, 'wb') as f:
            for block in response.iter_content(blocksize):
                f.write(block)
                count += len(block)
                if count > 100000:
                    count = 0
                    sys.stdout.write('.')
                    sys.stdout.flush()
            print
