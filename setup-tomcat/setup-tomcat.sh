#!/bin/bash

groupadd tomcat
useradd -g tomcat tomcat

echo tomcat | passwd -- stdin tomcat

yum -y install tomcat7

