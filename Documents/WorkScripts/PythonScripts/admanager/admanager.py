#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright [2016] the Kenzan Media authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
SYNOPSIS

    admanager.py

DESCRIPTION
    This is a restful service for creating users, and updating user passwords in active directory.
    
EXAMPLES

    coming soon.

EXIT STATUS

    Module will raise an exception on abnormal termination.

AUTHOR

    Grant Zukel

INITIAL VERSION

    21-Jan-16

COPYRIGHT

    This script is in owned and (C) 2013 by Grant Zukel.  All rights are reserved.
    Use of this program without written permission is prohibited.    

VERSION HISTORY
    
    1.0   Initial version

"""

import argparse
from bottle import route, run
import boto.route53
from boto import route53 
from ConfigParser import SafeConfigParser
from datetime import datetime
import json
import logging
import logging.config
from logging.handlers import RotatingFileHandler
import multiprocessing
import os
import re
import socket
from subprocess import Popen, PIPE
import sqlite3 as lite
import sys
import time
import unicodedata
import urllib
import ldap
import ldap
import ldap.modlist as modlist

def build_logger(name, path):
    
    logger = logging.getLogger(name)
    
    logger.setLevel(logging.INFO)
 
    file_name = name+".log"
    
    fh = RotatingFileHandler(path+file_name, mode="a", maxBytes=100*1024*1024, backupCount=10, encoding=None, delay=0)
 
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    
    return logger  

def create_user(ldap_client,username, password,email):   
    
    firstName = username.split('.')[0]
    
    lastName = username.split('.')[1]
    
    built_name = username
     
    dn="cn="+built_name+",cn=Users,dc=directory,dc=oneplatform,dc=net" 
    
    attrs = {}
    
    attrs['objectclass'] = ['Top','person','organizationalPerson','user']
    
    attrs['cn'] = built_name
    
    attrs['displayName'] = built_name
    
    attrs['name'] = lastName
    
    attrs['givenName'] = firstName
    
    attrs['mail'] = email
    
    attrs['ou'] = "Users"
    
    attrs['pwdLastSet'] = "-1"
    
    attrs['userPrincipalName'] = username + "@directory.oneplatform.net"
    
    attrs['sAMAccountName'] = username
    
    attrs['userPassword'] = password

    ldif = modlist.addModlist(attrs)
    
    ldap_client.add_s(dn,ldif)
    
    success_string = "success %s" % str(ldif)  
    
    return success_string

def update_credentials(ldap_client, username, old_password, new_password):

    firstName = username.split('.')[0]
    
    lastName = username.split('.')[1]
    
    built_name = username

    dn="cn=" + built_name + ",cn=Users,dc=directory,dc=oneplatform,dc=net"
    
    old = {"userPassword": old_password, "sAMAccountName": username}
    
    new = {"userPassword": new_password, "sAMAccountName": username}
    
    ldif = modlist.modifyModlist(old,new)
    
    ldap_client.modify_s(dn,ldif)
    
    success_string = "success %s" % str(ldif) 
    
    return success_string

def delete_user(ldap_client, username):

    deleteDN = "sAMAccountName="+username+",cn=Users,dc=directory,dc=oneplatform,dc=net"
    
    ldap_client.delete_s(deleteDN)
    
    success_string = "success %s" % str(deleteDN)  
    
    return success_string
    
def init_ldap_client():
    
    try:
        
        ldap_client = None
        
        username = "USERNAMESED"
        
        password = "PASSWORDSED"
        
        host = "HOSTSED"
        
        port = "PORTSED"
        
        domain = "DOMAINSED"
        
        LDAP_SERVER = "ldap://"+host+":"+port
        
        LDAP_USERNAME = ('%s@%s' % (username,domain))
        
        LDAP_PASSWORD = password
            
        ldap_filter = ('userPrincipalName=%s@%s' % (username,domain))
        
        attrs = ['memberOf']
            
        ldap_client = ldap.initialize(LDAP_SERVER)
        
        ldap_client.set_option(ldap.OPT_REFERRALS,0)
        
        ldap_client.simple_bind_s(LDAP_USERNAME, LDAP_PASSWORD)
        
        return ldap_client
    
    except ldap.INVALID_CREDENTIALS:
        
        ldap_client.unbind()
        
        return 'Wrong username ili password'
        
    except ldap.SERVER_DOWN:
        
        return 'AD server not awailable'

def start_local_server(port):
    
    #ip_address = socket.gethostbyname(socket.gethostname())
    ip_address = "localhost"
    run(host=ip_address, port=port, debug=False)
    
@route('/newuser/<name>', method='GET')
def new_user( name="Execute Cluster Registration" ):
    
    values = name.split('&')
    
    for value in values:
        
        new_split = value.split('=')
        
        if "username" in str(value):
            
            username = str(new_split[1])

        if "firstName" in str(value):
            
            firstName = str(new_split[1])

        if "lastName" in str(value):
            
            lastName = str(new_split[1])
            
        if "email" in str(value):
            
            email = str(new_split[1])
        
        if "password" in str(value):
            
            password = str(new_split[1])
    
    username = firstName + "." + lastName
    
    ldap_client = init_ldap_client()
    
    try:
        
        if "," in str(username):
            
            username.split(',')
            
            for user in username:
                
                success_ret = create_user(ldap_client,username, password, email) 
                
                success = "<li>Created user: %s</li>" % username
        else:
            
            success_ret = create_user(ldap_client,username, password, email) 
             
            success = "<li>Created user: %s</li>" % username 
    except:
        
        success_ret = create_user(ldap_client,username, password, email)
          
        success = "<li>Created user: %s</li>" % username
        
    ldap_client.unbind() 
    
    return success   

@route('/update/<name>', method='GET')
def update( name="Execute Cluster Registration" ):
    
    values = name.split('&')
    
    for value in values:
        
        new_split = value.split('=')
        
        if "firstName" in str(value):
            
            firstName = str(new_split[1])

        if "lastName" in str(value):
            
            lastName = str(new_split[1])
        
        if "old_password" in str(value):
            
            old_password = str(new_split[1])
        
        if "new_password" in str(value):
            
            new_password = str(new_split[1])
        
    
    username = firstName + "." + lastName
            
    ldap_client = init_ldap_client()
    
    try:
        
        success_ret = update_credentials(ldap_client, username, old_password, new_password)  
          
        success = "Password Changed Successfully"
        
    except Exception as e:
        success = "Failed to change password. Reason: " + str(e)
    
    ldap_client.unbind()
    
    return success


if os.path.exists("/var/log/adcontrol"):
    
    request_log = build_logger("request-log", "/var/log/adcontrol/")
    
if __name__ == '__main__':
        
    start_local_server("8001") 

