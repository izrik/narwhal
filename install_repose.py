#!/usr/bin/env python

import requests
import xml.etree.ElementTree as et
import xml.dom.minidom
import sys
import shutil
import os


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
            artifact_url = '%s/%s-%s.%s' % (version_root, artifact_id, value, extension)
            return artifact_url

    return None


def get_repose_valve_url(release=False):
    if release:
        s_or_r = 'releases'
    else:
        s_or_r = 'snapshots'

    root = "http://maven.research.rackspacecloud.com/content/repositories/%s/com/rackspace/papi/core/valve" % s_or_r

    return get_artifact_url(root, 'jar')


def get_filter_bundle_url(release=False):
    if release:
        s_or_r = 'releases'
    else:
        s_or_r = 'snapshots'

    root = "http://maven.research.rackspacecloud.com/content/repositories/%s" % s_or_r

    froot = '%s/com/rackspace/papi/components/filter-bundle' % root

    f_artifact_url = get_artifact_url(froot, 'ear')

    return f_artifact_url


def get_extensions_filter_bundle_url(release=False):
    if release:
        s_or_r = 'releases'
    else:
        s_or_r = 'snapshots'

    root = "http://maven.research.rackspacecloud.com/content/repositories/%s" % s_or_r

    eroot = "%s/com/rackspace/papi/components/extensions/extensions-filter-bundle" % root

    e_artifact_url = get_artifact_url(eroot, 'ear')

    return e_artifact_url


def download_file(url, filename=None):
    if filename is None:
        filename = url.split('/')[-1]

    create_folder(os.path.dirname(filename))

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


def delete_folder(folder_name):
    if os.path.exists(folder_name):
        shutil.rmtree(folder_name)


def blitz():
    delete_folder('var')
    delete_folder('etc')
    delete_folder('usr')


def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def init():
    create_folder('usr/share/repose/filters')
    create_folder('var/log/repose')
    create_folder('var/repose')
    create_folder('etc/repose')


def run():
    blitz()
    init()

    vurl = get_repose_valve_url()
    furl = get_filter_bundle_url()
    eurl = get_extensions_filter_bundle_url()

    print vurl
    if vurl:
        download_file(vurl, 'usr/share/repose/repose-valve.jar')

    print furl
    if furl:
        download_file(furl, 'usr/share/repose/filters/filter-bundle.ear')

    print eurl
    if eurl:
        download_file(eurl, 'usr/share/repose/filters/extensions-filter-bundle.ear')


if __name__ == '__main__':
    run()
