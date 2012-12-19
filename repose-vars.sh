#!/bin/bash

REPOSE_BASE=$REPOSE_FOLDER

if [ "$1" = "release" ]; then
  export REPOSE_SNAPSHOTS_RELEASES=releases
  export REPOSE_REPO_URL="http://maven.research.rackspacecloud.com/content/repositories/$REPOSE_SNAPSHOTS_RELEASES/org/atomhopper/$REPOSE_FOLDER"
  export REPOSE_VERSION=`curl -s $REPOSE_REPO_URL/maven-metadata.xml | xpath '//version[last()]/text()' 2>/dev/null`
  export REPOSE_BASENAME=$REPOSE_BASE-$REPOSE_VERSION
else
  export REPOSE_SNAPSHOTS_RELEASES=snapshots
  export REPOSE_REPO_URL="http://maven.research.rackspacecloud.com/content/repositories/$REPOSE_SNAPSHOTS_RELEASES/org/atomhopper/$REPOSE_FOLDER"
  export REPOSE_VERSION=`curl -s $REPOSE_REPO_URL/maven-metadata.xml | xpath '//version[last()]/text()' 2>/dev/null`
  REPOSE_BUILD_TIMESTAMP=`curl -s $REPOSE_REPO_URL/$REPOSE_VERSION/maven-metadata.xml | xpath '/metadata/versioning/snapshot/timestamp/text()' 2>/dev/null`
  REPOSE_BUILD_NUMBER=`curl -s $REPOSE_REPO_URL/$REPOSE_VERSION/maven-metadata.xml | xpath '/metadata/versioning/snapshot/buildNumber/text()' 2>/dev/null`
  REPOSE_BUILD=`curl -s $REPOSE_REPO_URL/$REPOSE_VERSION/maven-metadata.xml | xpath "//snapshotVersion[extension=\"$REPOSE_EXT\" and (not(classifier) or classifier/text() != 'sources')]/value/text()" 2>/dev/null`
  export REPOSE_BASENAME=$REPOSE_BASE-$REPOSE_BUILD
fi

if [ "$2" = "rpm" ]; then
  export REPOSE_FILE="${REPOSE_BASENAME}-rpm.rpm"
elif [ "$2" == "jetty" ]; then
  export REPOSE_FILE="${REPOSE_BASENAME}.jar"
else
  export REPOSE_FILE="${REPOSE_BASENAME}.war"
fi

export REPOSE_ARTIFACT_URL=$REPOSE_REPO_URL/$REPOSE_VERSION/$REPOSE_FILE


