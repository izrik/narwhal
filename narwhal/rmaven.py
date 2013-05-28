
import argparse
import logging
import maven

from . import __version__


logger = logging.getLogger(__name__)


class ReposeMavenConnector(maven.MavenConnector):
    _default_valve_dest = 'usr/share/repose/repose-valve.jar'
    _default_filter_dest = 'usr/share/repose/filters/filter-bundle.ear'
    _default_ext_filter_dest = ('usr/share/repose/filters/'
                                'extensions-filter-bundle.ear')

    def __init__(self, root=None):
        if root is None:
            root = ('maven.research.rackspacecloud.com/'
                    'content/repositories')
        maven.MavenConnector.__init__(self, root=root)

    def get_repose_valve_url(self, snapshot=False, version=None):
        path = 'com/rackspace/papi/core/valve'
        return self.get_repose_artifact_url(path=path, extension='jar',
                                            snapshot=snapshot, version=version)

    def get_filter_bundle_url(self, snapshot=False, version=None):
        path = 'com/rackspace/papi/components/filter-bundle'
        return self.get_repose_artifact_url(path=path, extension='ear',
                                            snapshot=snapshot, version=version)

    def get_extensions_filter_bundle_url(self, snapshot=False, version=None):
        path = ('com/rackspace/papi/components/extensions/'
                'extensions-filter-bundle')
        return self.get_repose_artifact_url(path=path, extension='ear',
                                            snapshot=snapshot, version=version)

    def get_repose_artifact_url(self, path, extension, snapshot=False,
                                version=None):
        if snapshot:
            s_or_r = 'snapshots'
        else:
            s_or_r = 'releases'
        new_path = '{0}/{1}'.format(s_or_r, path)
        return self.get_artifact_url(path=new_path, extension=extension,
                                     snapshot=snapshot, version=version)

    def get_repose(self, valve_dest=None, filter_dest=None,
                   ext_filter_dest=None, get_valve=True, get_filter=True,
                   get_ext_filter=True, snapshot=False, version=None):

        if valve_dest is None:
            valve_dest = ReposeMavenConnector._default_valve_dest
        if filter_dest is None:
            filter_dest = ReposeMavenConnector._default_filter_dest
        if ext_filter_dest is None:
            ext_filter_dest = ReposeMavenConnector._default_ext_filter_dest

        if get_valve:
            vurl = self.get_repose_valve_url(snapshot=snapshot,
                                             version=version)
        if get_filter:
            furl = self.get_filter_bundle_url(snapshot=snapshot,
                                              version=version)
        if get_ext_filter:
            eurl = self.get_extensions_filter_bundle_url(snapshot=snapshot,
                                                         version=version)

        filenames = {}

        if get_valve:
            valve_dest = self.clean_up_dest(vurl, valve_dest)
            print '%s --> %s' % (vurl, valve_dest)
            if vurl:
                self.download_file(url=vurl, dest=valve_dest)
                filenames["valve"] = valve_dest

        if get_filter:
            filter_dest = self.clean_up_dest(furl, filter_dest)
            print '%s --> %s' % (furl, filter_dest)
            if furl:
                self.download_file(url=furl, dest=filter_dest)
                filenames["filter"] = filter_dest

        if get_ext_filter:
            ext_filter_dest = self.clean_up_dest(eurl, ext_filter_dest)
            print '%s --> %s' % (eurl, ext_filter_dest)
            if eurl:
                self.download_file(url=eurl, dest=ext_filter_dest)
                filenames["ext_filter"] = ext_filter_dest

        return filenames
