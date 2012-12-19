#!/bin/bash

# this script will download and install the most recent version of repose
#   with the specified configuration

function log {
  echo '[' `date` '] ' $1 >> repose-setup.log
  echo '[' `date` '] ' $1
}

RELEASE=snapshot
SRC=war
CONF=

command_name=$0
function print_usage {
  echo "Usage: " `basename $command_name` "[ARG]..." 1>&2
  echo "where ARG can be zero or more of the following:" 1>&2
  echo "    release    - install the latest release build" 1>&2
  echo "    snapshot   - install the latests snapshot build" 1>&2
  echo "    war        - install by copying the WAR file into tomcat's webapps folder as ROOT.war" 1>&2
  echo "    rpm        - install by running the RPM file via yum" 1>&2
  echo "    jetty      - install by running the embedded Jetty JAR file as a background process" 1>&2
  echo "" 1>&2
}

if [ "$1" == "--help" ]; then
  print_usage
  exit 0
fi

for arg in "$@"
do
  if [ "$arg" == "release" ]; then 
    RELEASE=release
  elif [ "$arg" == "snapshot" ]; then
    RELEASE=snapshot
  elif [ "$arg" == "war" ]; then
    SRC=war
  elif [ "$arg" == "rpm" ]; then
    SRC=rpm
  elif [ "$arg" == "jetty" ]; then
    SRC=jetty
  else
    echo "Unknown arg \"$arg\""
    print_usage
    exit 1
  fi
done

### calculate variables and urls

function get_artifact_url_from_nexus {

  local REPOSE_FOLDER
  local REPOSE_EXT
  local REPOSE_BASE
  local REPOSE_SNAPSHOTS_RELEASES
  local REPOSE_REPO_URL
  local REPOSE_VERSION
  local REPOSE_BASENAME
  local REPOSE_BUILD_TIMESTAMP
  local REPOSE_BUILD_NUMBER
  local REPOSE_BUILD

  if [ "$2" == "jetty" ]; then
    REPOSE_FOLDER=ah-jetty-server
  else
    REPOSE_FOLDER=atomhopper
  fi

  if [ "$2" = "rpm" ]; then
    REPOSE_EXT=rpm
  elif [ "$2" == "war" ]; then
    REPOSE_EXT=war
  else
    REPOSE_EXT=jar
  fi
  REPOSE_BASE=$REPOSE_FOLDER

  if [ "$1" = "release" ]; then
    REPOSE_SNAPSHOTS_RELEASES=releases
    REPOSE_REPO_URL="http://maven.research.rackspacecloud.com/content/repositories/$REPOSE_SNAPSHOTS_RELEASES/org/atomhopper/$REPOSE_FOLDER"
    REPOSE_VERSION=`curl -s $REPOSE_REPO_URL/maven-metadata.xml | xpath '//version[last()]/text()' 2>/dev/null`
    REPOSE_BASENAME=$REPOSE_BASE-$REPOSE_VERSION
  else
    REPOSE_SNAPSHOTS_RELEASES=snapshots
    REPOSE_REPO_URL="http://maven.research.rackspacecloud.com/content/repositories/$REPOSE_SNAPSHOTS_RELEASES/org/atomhopper/$REPOSE_FOLDER"
    REPOSE_VERSION=`curl -s $REPOSE_REPO_URL/maven-metadata.xml | xpath '//version[last()]/text()' 2>/dev/null`
    REPOSE_BUILD_TIMESTAMP=`curl -s $REPOSE_REPO_URL/$REPOSE_VERSION/maven-metadata.xml | xpath '/metadata/versioning/snapshot/timestamp/text()' 2>/dev/null`
    REPOSE_BUILD_NUMBER=`curl -s $REPOSE_REPO_URL/$REPOSE_VERSION/maven-metadata.xml | xpath '/metadata/versioning/snapshot/buildNumber/text()' 2>/dev/null`
    REPOSE_BUILD=`curl -s $REPOSE_REPO_URL/$REPOSE_VERSION/maven-metadata.xml | xpath "//snapshotVersion[extension=\"$REPOSE_EXT\" and (not(classifier) or classifier/text() != 'sources')]/value/text()" 2>/dev/null`
    REPOSE_BASENAME=$REPOSE_BASE-$REPOSE_BUILD
  fi

  if [ "$2" = "rpm" ]; then
    REPOSE_FILE="${REPOSE_BASENAME}-rpm.rpm"
  elif [ "$2" == "jetty" ]; then
    REPOSE_FILE="${REPOSE_BASENAME}.jar"
  else
    REPOSE_FILE="${REPOSE_BASENAME}.war"
  fi

  local REPOSE_ARTIFACT_URL=$REPOSE_REPO_URL/$REPOSE_VERSION/$REPOSE_FILE

  return $REPOSE_ARTIFACT_URL
}

ARTIFACT_URL=get_artifact_url_from_nexus $RELEASE $SRC

source ./catalina-vars.sh

### log the setup attempt
log "`basename $0` - RELEASE=$RELEASE, SRC=$SRC, CONF=$CONF, ARTIFACT_URL=$ARTIFACT_URL"

service tomcat7 stop
java -jar jetty-killer.jar &>/dev/null    # shutdown any ah jetty
sleep 3

# clean out the database
./blitz-ah.sh no-restart-tomcat

### tear down any previous versions

# uninstall any rpm
yum erase -y -q atomhopper.noarch

# uninstall any WAR file
rm -rf $CATALINA_HOME/webapps/ROOT.war
rm -rf $CATALINA_HOME/webapps/ROOT

# remove any jetty files
#

# delete left-over config files
rm -rf /etc/atomhopper
rm -rf /var/log/atomhopper

rm -rf $REPOSE_FILE

wget -q $ARTIFACT_URL

### install the newest version based on the desired deployment mechanism
if [ "$SRC" == "war" ] ; then

  mkdir -p /etc/atomhopper
  mkdir -p /var/log/atomhopper
  chown -R tomcat:tomcat /etc/atomhopper /var/log/atomhopper

  mv $REPOSE_FILE $CATALINA_HOME/webapps/
  rm -rf $CATALINA_HOME/webapps/ROOT/
  mv $CATALINA_HOME/webapps/$REPOSE_FILE $CATALINA_HOME/webapps/ROOT.war

elif [ "$SRC" == "rpm" ]; then

  if [ -e /srv/tomcat -a ! -L /srv/tomcat ]; then
    rm -rf /srv/tomcat
  fi
  if [ -e /srv/tomcat7 -a ! -L /srv/tomcat7 ]; then
    rm -rf /srv/tomcat7
  fi

  ln -s /usr/share/tomcat7/ /srv/tomcat7
  ln -s /usr/share/tomcat7/ /srv/tomcat

  yum install --nogpgcheck -y -q $REPOSE_FILE

elif [ "$SRC" == "jetty" ]; then

  mkdir -p /etc/atomhopper
  mkdir -p /var/log/atomhopper
  chown -R tomcat:tomcat /etc/atomhopper /var/log/atomhopper

fi

if [ "$CONF" -ne "" ]; then
### copy config files
./conf.pl $CONF --no-restart-tomcat --param hostname=`./calc-ip.sh`

# start up
if [ "$SRC" != "jetty" ]; then
  service tomcat7 start
else
  java -jar $REPOSE_FILE start &>/var/log/atomhopper/jetty.log &
fi

sleep 3
curl -s localhost:8080/namespace/feed


