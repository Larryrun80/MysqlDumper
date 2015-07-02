#!/usr/bin/env python
# Filename: mysqldumper.py

###########################################################
#
# This python script is used for mysql database backup
# for mysql version above 5.6
#
# Written by : Larry Guo
# Created date: June 29, 2015
# Last modified: June 29, 2015
# Tested with : Python 3.4.3
# Script Revision: 1.0
#
##########################################################

from configparser import ConfigParser
import os
import time
import subprocess
import sys


# Defining method to unify format of output info
def print_log(log_text):
    log_prefix = '[{0}]'.format(time.strftime('%Y-%m-%d %H:%M:%S'))
    print(('{0}{1}').format(log_prefix, log_text))

# Config file to get To-Backup database(s) info
# You can assign multi database info in config file
# Remember using same format as following:

# [DB_NAME_TO_BACKUP]
# Host = localhost
# User = username
# Password = password
# Database = database
# PORT = 3306
# Need_Restore = 1
# Ignore_Tables = tab_a, tab_b, tab_c,
#                 tab_d, tab_e, tab_f,
#                 tab_g, tab_h
# SSH_Tunnel = user@host_ip_address

# PORT, Ignore_Tables, SSH_Tunnel is not a must required config
# Need_Restore: if you want to restore database after it is backuped,
#               set Need_Restore as 'yes', else keep it 'no'
#               remember to add restore settings below if you choose yes
# Ignore_Tables: if you want to ignore some tables in backup progress,
#                use ',' to seperate them
# SSH_Tunnel: if database must be visited via a ssh tunnel, write a
#             "username@host_ip" format string to enable it
#             this function is now only support tunnels via ssh key
# Make sure you assigned accounts with enough proviliegesleges

# Remember to keep a restore section if you want to restore some dbs after
# backup, using following example:

# [RESTORE_SETTINGS]
# Host = localhost
# User = username
# Password = password
# PORT = 3306
# Prefix =

# Notice that the section name must be "RESTORE_SETTINGS"
# the databases will be restored with Prefix_OriginName
# so if you want to back up with origin name, leave Prefix option blank
# make sure you created the same databses on your restore mysql
# and make sure your account have the appropraite provilieges
# PORT option is optional if you are using 3306
CONFIG_FILE = 'conf/mysqldumper.conf'
DB_MUST_OPTIONS = ('Host', 'User', 'Password', 'Database', 'Need_Restore')
# Using Restore_DBs to save dabases want to be restored
Restore_DBs = []
RESTORE_MUST_OPTIONS = ('Host', 'User', 'Password', 'Prefix')

# Define the base back up folder
# And generate real-time backup folder using current datetime
BACKUP_PATH = os.path.abspath(os.path.dirname(__file__)) + '/backup/'
TODAY_BACKUP_PATH = BACKUP_PATH + time.strftime('%Y%m%d-%H%M%S')

print('============== START BACKUP ON {0} =============='
      .format(time.strftime('%Y-%m-%d %H:%M:%S')))
# Checking if backup folder already exists. Create it if not.
print_log("checking backup folder")
if not os.path.exists(TODAY_BACKUP_PATH):
    os.makedirs(TODAY_BACKUP_PATH)
    print_log('created backup folder: {0}'.format(TODAY_BACKUP_PATH))
else:
    print_log('backup folder found at {0}'.format(TODAY_BACKUP_PATH))

try:
    # Geting databases and backup
    config = ConfigParser()
    config.read(CONFIG_FILE)
    for database in config.sections():
        if database != 'RESTORE_SETTINGS':
            print_log('checking and back up database: {0}'.format(database))

            # Checking if all options needed had been set
            legal_section = True
            for must_option in DB_MUST_OPTIONS:
                if not config.has_option(database, must_option):
                    print_log('{0} not found in {1} section, skipped'
                              .format(must_option, database))
                    legal_section = False
                    break

            # Backuping
            if legal_section:
                # build command to exec
                dumpcmd = "MYSQL_PWD="\
                          + config.get(database, 'Password') \
                          + " mysqldump -h"\
                          + config.get(database, 'Host') \
                          + " -u" \
                          + config.get(database, 'User') \
                          + " " \
                          + config.get(database, 'Database')
                # if with port config
                if config.has_option(database, 'Port'):
                    if config.get(database, 'Port') \
                             .replace('\r', '') \
                             .replace('\n', '') \
                             .replace(' ', '') \
                             != '':
                        dumpcmd += " -P" \
                                + config.get(database, 'Port')
                # if with ignore config
                if config.has_option(database, 'Ignore_Tables'):
                    ignore_tables = config.get(database,
                                               'Ignore_Tables') \
                                               .replace('\r', '') \
                                               .replace('\n', '') \
                                               .replace(' ', '') \
                                               .split(',')
                    for table in ignore_tables:
                        dumpcmd += " --ignore-table=" \
                                   + config.get(database, 'Database') \
                                   + "." \
                                   + table
                # add set gtid option (for mysql5.6) and complete command
                dumpcmd += " --set-gtid-purged=OFF " \
                           + "--single-transaction --quick" \
                           + "  > " \
                           + TODAY_BACKUP_PATH \
                           + "/" \
                           + config.get(database, 'Database') \
                           + ".sql"

                # using ssh tunnel if needed
                if config.has_option(database, 'SSH_Tunnel'):
                    if config.get(database, 'SSH_Tunnel') \
                             .replace('\r', '') \
                             .replace('\n', '') \
                             .replace(' ', '') \
                             != '':
                        dumpcmd = 'ssh ' \
                                  + config.get(database, 'SSH_Tunnel') \
                                  + ' ' \
                                  + dumpcmd

                # Open this if you want to debug the command
                # print_log(dumpcmd)

                # executing backup command
                try:
                    subprocess.check_call(dumpcmd, shell=True)
                    # if this database needs restore, add to list
                    if config.get(database, 'Need_Restore') == 'yes':
                        Restore_DBs.append(config.get(database,
                                           'Database'))
                    print_log('backup {0} successed'.format(database))
                except subprocess.CalledProcessError as e:
                    print_log('error found, backup and restore terminated')

    # Checking is some databases needs restore
    if len(Restore_DBs) > 0:
        # Checking all options restore db needed had been set
        legal_restore_info = True
        for must_option in RESTORE_MUST_OPTIONS:
            if not config.has_option('RESTORE_SETTINGS', must_option):
                print_log('{0} not found in restore section,\
                           skipped'.format(must_option))
                legal_restore_info = False
        # Starting restore
        if legal_restore_info:
            for db_name in Restore_DBs:
                print_log('start restoring databases {0}'.format(db_name))
                # generating back up database name
                backup_name = config.get('RESTORE_SETTINGS', 'Prefix') \
                                    .replace(' ', '') + '_' + db_name
                if backup_name[0] == '_':
                    backup_name = db_name

                # generating restore command to exec
                restorecmd = "MYSQL_PWD="\
                             + config.get('RESTORE_SETTINGS', 'Password') \
                             + " mysql -h"\
                             + config.get('RESTORE_SETTINGS', 'Host') \
                             + " -u" \
                             + config.get('RESTORE_SETTINGS', 'User') \
                             + " " \
                             + backup_name \
                             + " < " \
                             + TODAY_BACKUP_PATH \
                             + "/" \
                             + db_name \
                             + ".sql"

                # Open this if you want to debug the command
                # print_log(restorecmd)

                # executing restore command
                try:
                    subprocess.check_call(restorecmd, shell=True)
                    print_log('restore {0} successed'.format(db_name))
                except subprocess.CalledProcessError as e:
                    print_log('error found, restore terminated')
except:
    print_log('%s: %s', str(sys.exc_info()[0]), str(sys.exc_info()[1]))
