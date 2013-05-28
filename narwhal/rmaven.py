
import argparse
import logging
import maven

from . import __version__


logger = logging.getLogger(__name__)


class ReposeMavenConnector(maven.MavenConnector):
    def __init__(self, root=None):
        if root is None:
            root = ('maven.research.rackspacecloud.com/'
                    'content/repositories')
        maven.MavenConnector.__init__(self, root=root)

    def get_repose_artifact_url(self, path, extension, snapshot=False,
                                version=None):
        if snapshot:
            s_or_r = 'snapshots'
        else:
            s_or_r = 'releases'
        new_path = '{0}/{1}'.format(s_or_r, path)
        return self.get_artifact_url(path=new_path, extension=extension,
                                     snapshot=snapshot, version=version)
