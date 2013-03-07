#!/bin/bash

REPO_BASE=https://github.com/richard-sartor/
REPO_FOLDER=narwhal
REPO_SUFFIX=.git

if [ -e .git ]; then
  git pull origin master
elif [ -e $REPO_FOLDER ]; then
  if [ -e $REPO_FOLDER/.git ]; then
    cd $REPO_FOLDER
    git pull origin master
  else
    echo "Can't clone the repo." >&2
    exit 1
  fi
else
  git clone "$REPO_BASE$REPO_FOLDER$REPO_SUFFIX"
  cd $REPO_FOLDER
fi

if [ "$1" == "checkout" ]
then
  shift
  BRANCH=$1
  git checkout $BRANCH
  shift
fi


