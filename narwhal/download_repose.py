#!/usr/bin/env python

import argparse
import os
import shutil
import sys
import xml.dom.minidom
import xml.etree.ElementTree as et
import requests
import pathutil
import re
import logging


logger = logging.getLogger(__name__)


def get_artifact_url(root, extension, snapshot=False, version=None):

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
                    raise Exception('Invalid version format: "%s"' % version)
                main_version = m.group(1)
                snapshot_version = '%s-%s' % (main_version, m.group(2))
            found = False
            for vv in metax.findall('versioning/versions/version'):
                # kludge - searching through the list because ET doesn't have
                # complete xpath predicate support
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
                # kludge - searching through the list because ET doesn't have
                # complete xpath predicate support
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


def clean_up_dest(url, dest=None):
    """Clean up the destination. If dest is None, use the filename of the file
    being downloaded and store it in the current directory. If dest ends with a
    '/', or if it points to a directory, use the filename of the file being
    downloaded and store it in the specified directory. If dest doesn't end
    with a '/' and doesn't point to a directory, store the file using the
    specfied filename. If the specified already exists, append a number to
    it."""
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
            logger.debug('os.path.exists(os.path.join(dirname, basename2)): %s'
                         % os.path.exists(os.path.join(dirname, basename2)))
            while os.path.exists(os.path.join(dirname, basename2)):
                basename2 = basename + '.%i' % n
                n += 1
                logger.debug('basename2: %s' % basename2)
                logger.debug('os.path.exists(os.path.join(dirname, '
                             'basename2)): %s' %
                             os.path.exists(os.path.join(dirname, basename2)))
            basename = basename2
        dest = os.path.join(dirname, basename)
        logger.debug('dest [final]: %s' % dest)
    return dest


def download_file(url, dest):

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


_default_url_root = ('http://maven.research.rackspacecloud.com/'
                     'content/repositories')
_default_valve_dest = 'usr/share/repose/repose-valve.jar'
_default_filter_dest = 'usr/share/repose/filters/filter-bundle.ear'
_default_ext_filter_dest = ('usr/share/repose/filters/'
                            'extensions-filter-bundle.ear')


def get_repose_valve_url(root, snapshot=False, version=None):
    if snapshot:
        s_or_r = 'snapshots'
    else:
        s_or_r = 'releases'

    vroot = "%s/%s/com/rackspace/papi/core/valve" % (root, s_or_r)

    return get_artifact_url(vroot, 'jar', snapshot=snapshot, version=version)


def get_filter_bundle_url(root, snapshot=False, version=None):
    if snapshot:
        s_or_r = 'snapshots'
    else:
        s_or_r = 'releases'

    froot = ('%s/%s/com/rackspace/papi/components/filter-bundle' %
             (root, s_or_r))

    f_artifact_url = get_artifact_url(froot, 'ear', snapshot=snapshot,
                                      version=version)

    return f_artifact_url


def get_extensions_filter_bundle_url(root, snapshot=False, version=None):
    if snapshot:
        s_or_r = 'snapshots'
    else:
        s_or_r = 'releases'

    eroot = ("%s/%s/com/rackspace/papi/components/extensions/"
             "extensions-filter-bundle" % (root, s_or_r))

    e_artifact_url = get_artifact_url(eroot, 'ear', snapshot=snapshot,
                                      version=version)

    return e_artifact_url


def get_repose(url_root=None, valve_dest=None, filter_dest=None,
               ext_filter_dest=None, get_valve=True, get_filter=True,
               get_ext_filter=True, snapshot=False, version=None):

    if url_root is None:
        url_root = _default_url_root
    if valve_dest is None:
        valve_dest = _default_valve_dest
    if filter_dest is None:
        filter_dest = _default_filter_dest
    if ext_filter_dest is None:
        ext_filter_dest = _default_ext_filter_dest

    if get_valve:
        vurl = get_repose_valve_url(root=url_root, snapshot=snapshot,
                                    version=version)
    if get_filter:
        furl = get_filter_bundle_url(root=url_root, snapshot=snapshot,
                                     version=version)
    if get_ext_filter:
        eurl = get_extensions_filter_bundle_url(root=url_root,
                                                snapshot=snapshot,
                                                version=version)

    filenames = {}

    if get_valve:
        valve_dest = clean_up_dest(vurl, valve_dest)
        print '%s --> %s' % (vurl, valve_dest)
        if vurl:
            download_file(url=vurl, dest=valve_dest)
            filenames["valve"] = valve_dest

    if get_filter:
        filter_dest = clean_up_dest(furl, filter_dest)
        print '%s --> %s' % (furl, filter_dest)
        if furl:
            download_file(url=furl, dest=filter_dest)
            filenames["filter"] = filter_dest

    if get_ext_filter:
        ext_filter_dest = clean_up_dest(eurl, ext_filter_dest)
        print '%s --> %s' % (eurl, ext_filter_dest)
        if eurl:
            download_file(url=eurl, dest=ext_filter_dest)
            filenames["ext_filter"] = ext_filter_dest

    return filenames


def run():

    parser = argparse.ArgumentParser()
    parser.add_argument('--valve-dest', help='The name that the Valve JAR '
                        'should be renamed to, or the directory where it '
                        'should be downloaded to.')
    parser.add_argument('--filter-dest', help='The name that the filter '
                        'bundle EAR file should be renamed to, or the '
                        'directory where it should be downloaded to.')
    parser.add_argument('--ext-filter-dest', help='The name that the '
                        'extension filter bundle EAR file should be renamed '
                        'to, or the directory where it should be downloaded '
                        'to.')
    parser.add_argument('--no-valve',
                        help='Don\'t download the valve JAR file',
                        action='store_true')
    parser.add_argument('--no-filter', help='Don\'t download the standard '
                        'filter bundle EAR file', action='store_true')
    parser.add_argument('--no-ext-filter', help='Don\'t download the '
                        'extension filter bundle EAR file',
                        action='store_true')
    parser.add_argument('--url-root', help='The url (with path) to download '
                        'artifacts from.',
                        default=_default_url_root)
    parser.add_argument('--snapshot', help='Download a SNAPSHOT build instead '
                        'of a release build.', action='store_true')
    parser.add_argument('--version', help='The version of the artifacts to '
                        'download. Typically of the forms "x.y.z" for '
                        'releases, "x.y.z-SNAPSHOT" for the most recent '
                        'snapshot build in version x.y.z, and '
                        '"x.y.z-date.time-build" for a specific snapshot '
                        'build.', type=str)
    parser.add_argument('--print-log', help="Print the log to STDERR.",
                        action='store_true')
    parser.add_argument('--full-log', help="Log more information.",
                        action='store_true')
    args = parser.parse_args()

    if args.print_log:
        if args.full_log:
            logging.basicConfig(level=logging.DEBUG,
                                format='%(levelname)s:%(name)s:%(funcName)s:'
                                '%(filename)s(%(lineno)d):%(threadName)s'
                                '(%(thread)d):%(message)s')
        else:
            logging.basicConfig(level=logging.DEBUG)

    get_repose(url_root=args.url_root, valve_dest=args.valve_dest,
               filter_dest=args.filter_dest,
               ext_filter_dest=args.ext_filter_dest,
               get_valve=not args.no_valve, get_filter=not args.no_filter,
               version=args.version, get_ext_filter=not args.no_ext_filter,
               snapshot=args.snapshot)


if __name__ == '__main__':
    run()
