#!/usr/bin/env python

import pyrax
import os
import argparse
import time
import paramiko
import getpass

# TODO: get credentials from command line
pyrax.set_credential_file(os.path.expanduser('~/repose2.creds'))

cs = pyrax.cloudservers

centos_image = [img for img in cs.images.list() if "CentOS 6.3" in img.name][0]
flavor = [f for f in cs.flavors.list() if f.ram == 1024][0]

t = time.localtime()
date_string = '%d-%02d-%02d-%02d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday,
                                               t.tm_hour, t.tm_min, t.tm_sec)
name_prefix = 'repose-qe-test-prevent-xxe'
whoami = getpass.getuser()
server_name = '%s-%s-%s' % (name_prefix, date_string, whoami)

server = cs.servers.create(name=server_name,
                           image=centos_image, flavor=flavor)

print time.asctime()
n = 0
while n < 600:
    server2 = cs.servers.get(server.id)
    if server2.status == u'ACTIVE':
        break
    if server2.status != u'BUILD' and server2.status != u'UNKNOWN':
        raise Exception("Server entered an invalid state: '%s'" %
                        server.status)
    time.sleep(15)
    print time.asctime()
    n += 15

if server2.status != u'ACTIVE':
    raise Exception('Server failed to build in time')

username = 'root'
password = server.adminPass
print 'password: %s' % password
ips = server2.networks['public']

os.system('ssh-keyscan %s 2>/dev/null >> ~/.ssh/known_hosts' % ' '.join(ips))

ssh_client = paramiko.SSHClient()
ssh_client.load_system_host_keys()

connected = False

for ip in ips:
    try:
        ssh_client.connect(hostname=ip, username=username, password=password)
        connected = True
        break
    except:
        pass

if not connected:
    raise Exception("Could not connect")


def readfile(file):
    try:
        return file.read()
    except:
        return None

def exec_command2(command, bufsize=-1):
    return map(readfile, ssh_client.exec_command(command, bufsize))

epel_filename = 'epel-release-6-8.noarch.rpm'
epel_url = ('http://download.fedoraproject.org/pub/epel/6/i386/%s' %
            epel_filename)

stdio = exec_command2('wget %s' % epel_url)
stdio = exec_command2('rpm -Uvh %s' % epel_filename)
stdio = exec_command2('rm -f %s' % epel_filename)

stdio = exec_command2('yum install -y python python-pip git')

stdio = exec_command2('pip-python install virtualenv')


