#!/usr/bin/env python

import argparse
import os
import shutil
import sys
import xml.dom.minidom
import xml.etree.ElementTree as et
import requests
import pathutil


def get_artifact_url(root, extension):
    meta = '%s/maven-metadata.xml' % root
    metas = requests.get(meta).text
    metax = et.fromstring(metas)
    artifact_id = metax.find('artifactId').text
    latest = metax.find('versioning/latest').text
    version_root = '%s/%s' % (root, latest)
    meta2 = '%s/maven-metadata.xml' % version_root
    meta2s = requests.get(meta2).text
    meta2x = et.fromstring(meta2s)
    last_updated = meta2x.find('versioning/lastUpdated').text
    for elem in meta2x.findall('versioning/snapshotVersions/snapshotVersion'):
        if (elem.find('extension').text == extension and
                elem.find('updated').text == last_updated):

            value = elem.find('value').text
            artifact_url = '%s/%s-%s.%s' % (version_root, artifact_id, value,
                                            extension)
            return artifact_url

    return None


def get_repose_valve_url(root, release=False):
    if release:
        s_or_r = 'releases'
    else:
        s_or_r = 'snapshots'

    vroot = "%s/%s/com/rackspace/papi/core/valve" % (root, s_or_r)

    return get_artifact_url(vroot, 'jar')


def get_filter_bundle_url(root, release=False):
    if release:
        s_or_r = 'releases'
    else:
        s_or_r = 'snapshots'

    froot = ('%s/%s/com/rackspace/papi/components/filter-bundle' %
             (root, s_or_r))

    f_artifact_url = get_artifact_url(froot, 'ear')

    return f_artifact_url


def get_extensions_filter_bundle_url(root, release=False):
    if release:
        s_or_r = 'releases'
    else:
        s_or_r = 'snapshots'

    eroot = ("%s/%s/com/rackspace/papi/components/extensions/"
             "extensions-filter-bundle" % (root, s_or_r))

    e_artifact_url = get_artifact_url(eroot, 'ear')

    return e_artifact_url


def download_file(url, filename=None):
    if filename is None:
        filename = url.split('/')[-1]

    pathutil.create_folder(os.path.dirname(filename))

    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError

    blocksize = 4096
    count = 0
    with open('./%s' % filename, 'wb') as f:
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
_default_valve_dest = 'usr/share/repose'
_default_ear_dest = 'usr/share/repose/filters'

def get_repose(url_root=None, valve_dest=None, ear_dest=None, get_valve=True,
               get_filter=True, get_ext_filter=True):

    if url_root is None:
        url_root = _default_url_root
    if valve_dest is None:
        valve_dest = _default_valve_dest
    if ear_dest is None:
        ear_dest = _default_ear_dest

    if get_valve:
        vurl = get_repose_valve_url(url_root)
    if get_filter:
        furl = get_filter_bundle_url(url_root)
    if get_ext_filter:
        eurl = get_extensions_filter_bundle_url(url_root)

    if get_valve:
        print vurl
        if vurl:
            download_file(vurl, os.path.join(valve_dest, 'repose-valve.jar'))

    if get_filter:
        print furl
        if furl:
            download_file(furl, os.path.join(ear_dest, 'filter-bundle.ear'))

    if get_ext_filter:
        print eurl
        if eurl:
            download_file(eurl, os.path.join(ear_dest,
                                             'extensions-filter-bundle.ear'))


def run():

    parser = argparse.ArgumentParser()
    parser.add_argument('--valve-dest', help='Folder where you want the '
                        'repose-valve.jar file to go.',
                        default=_default_valve_dest)
    parser.add_argument('--ear-dest', help='Folder where you want the EAR '
                        'filter bundles to go.',
                        default=_default_ear_dest)
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
    args = parser.parse_args()

    get_repose(url_root=args.url_root, valve_dest=args.valve_dest,
               ear_dest=args.ear_dest, get_valve=not args.no_valve,
               get_filter=not args.no_filter,
               get_ext_filter=not args.no_ext_filter)


if __name__ == '__main__':
    run()
