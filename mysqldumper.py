#!/usr/bin/env python
# Filename: mysqldumper.py

###########################################################
#
# This python script is used for mysql database backup
#
# Written by : Larry Guo
# Created date: June 29, 2015
# Last modified: July 10, 2015
# Tested with : Python 3.4.3
# Script Revision: 2.0
#
##########################################################

from configparser import ConfigParser
import datetime
import os
import time
import shutil
import subprocess
import sys


# Defining method to unify format of output info
def print_log(log_text):
    log_prefix = '[{0}]'.format(time.strftime('%Y-%m-%d %H:%M:%S'))
    print(('{0} {1}').format(log_prefix, log_text))


# Return a boolean to indicate whether the sqldump command needs a
# gtid option. this option is needed from mysql version 5.6
def need_gtid():
    try:
        mysql_output = subprocess.check_output('mysql -V', shell=True).decode()
        start_pos = mysql_output.find('Distrib') + len('Distrib') + 1
        tmp_str_array = mysql_output[start_pos:].split('.')
        mysql_ver = '{0}.{1}'.format(tmp_str_array[0], tmp_str_array[1])
        if (type(eval(mysql_ver)) == float) and (float(mysql_ver) >= 5.6):
            return True
        else:
            return False
    except:
        return False


# Delete former backup files
# pass a date format date
def del_backup():
    # If found backup dir, do
    if os.path.exists(TODAY_BACKUP_PATH):
        # get the start pos of the time string in backup dir name
        date_pos = BACKUP_DIRNAME.find(time.strftime(TIME_FORMAT))
        if date_pos == -1:
            print_log("defined dir name is invalid, clean up terminated")
            return
        else:
            # get a valid backuped dirname
            prefix = BACKUP_DIRNAME[0:date_pos]
            # for every dir in your backup path
            # check if its too old
            for dirname in os.listdir(BACKUP_PATH):
                if dirname.find(prefix) == 0:
                    try:
                        end_pos = date_pos+len(time.strftime(TIME_FORMAT))
                        date_str = dirname[date_pos:end_pos]
                        keep_days = datetime.timedelta(days=KEEP_DATA_PERIOD)
                        created_date = datetime.datetime.strptime(date_str,
                                                                  TIME_FORMAT)
                        if created_date < datetime.datetime.today()-keep_days:
                            # delete backuped dir and files if its old enough
                            del_dir = BACKUP_PATH + dirname
                            shutil.rmtree(del_dir)
                            print_log("deleted backup files in: {0}"
                                      .format(del_dir))
                    except:
                        # wrong dir name found
                        # for we can not recognize date string in dir name
                        print_log("wrong format found on folder {0},"
                                  " passed".format(dirname))

# ################################
# ##### START OF CONFIG PART #####
# ################################

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
# so if you want to bacup with origin name, leave Prefix option blank
# make sure you created the same databses on your restore mysql
# and make sure your account have the appropraite provilieges
# PORT option is optional if you are using 3306
CONFIG_FILE = os.path.abspath(os.path.dirname(__file__)) \
              + '/conf/mysqldumper.conf'
DB_MUST_OPTIONS = ('Host', 'User', 'Password', 'Database', 'Need_Restore')
# Using Restore_DBs to save dabases want to be restored
Restore_DBs = []
RESTORE_MUST_OPTIONS = ('Host', 'User', 'Password', 'Prefix')

# Define your favorite time format, it needs to obey python's strftime format
# this info will be used in backup directory name
# suggest you keep year, month, date info at least, especially if you'd like to
# let program delete overdue backuped data.
TIME_FORMAT = '%Y%m%d-%H%M%S'

# Define the base backup folder and bake up file name
# generate real-time backup folder and file using current datetime
BACKUP_PATH = os.path.abspath(os.path.dirname(__file__)) + '/backup/'
BACKUP_DIRNAME = 'db-' + time.strftime(TIME_FORMAT)
TODAY_BACKUP_PATH = BACKUP_PATH + BACKUP_DIRNAME

# Define the period the program will keep backup data
# program will delete backuped data before this date
# keep this paramater as -1 if you do not want to delete any backuped data
# make sense that you must have a date information is your backup directory
KEEP_DATA_PERIOD = 7

# Debug mode, if you turns this option to "True", MysqlDumper will print
# backup command and restore command(if there are any dbs to be restored)
DEBUG_MODE = False

# You can design some bash command to exec before restore
# This command will not be executed if you won't restore any database
# You can use "&&" if you want to execute multi commands
# Make sure the command will be operate correctly in bash
# Keep it '' if you do not need execute anything
PRERESTORE_COMMAND = '''

'''

# ##############################
# ##### END OF CONFIG PART #####
# ##############################

print('''
#################################################################
============== START BACKUP ON {0} ==============
#################################################################

      '''
      .format(time.strftime('%Y-%m-%d %H:%M:%S')))

# Cleaning former backuped data
if not isinstance(KEEP_DATA_PERIOD, int) or KEEP_DATA_PERIOD < -1:
    print_log("wrong format of KEEP_DATA_PERIOD,"
              " needs to be int and larger than -1, skip clean data stage")
elif KEEP_DATA_PERIOD != -1:
    print_log("start cleaning up data backuped before {0} days"
              .format(KEEP_DATA_PERIOD))
    del_backup()

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
    if not os.path.exists(CONFIG_FILE):
        print_log('Config file not found at: {0}, exit'
                  .format(os.path.abspath(CONFIG_FILE)))
        sys.exit()
    config.read(CONFIG_FILE)
    for database in config.sections():
        if database != 'RESTORE_SETTINGS':
            print_log('checking and backuping database: {0}'.format(database))

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
                if need_gtid():
                    dumpcmd += " --set-gtid-purged=OFF "

                dumpcmd += "--single-transaction --quick" \
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

                if DEBUG_MODE:
                    print_log(dumpcmd)

                # executing backup command
                try:
                    subprocess.check_call(dumpcmd,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
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
            # Execute any bash commands if needs
            if PRERESTORE_COMMAND is not None and PRERESTORE_COMMAND != '':
                try:
                    subprocess.check_call(PRERESTORE_COMMAND,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
                except subprocess.CalledProcessError as e:
                    print_log('error found when execute pre-restore command: \
                               {0}'.format(PRERESTORE_COMMAND))

            # Restoring dbs
            for db_name in Restore_DBs:
                print_log('start restoring databases {0}'.format(db_name))
                # generating backup database name
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

                if DEBUG_MODE:
                    print_log(restorecmd)

                # executing restore command
                try:
                    subprocess.check_call(restorecmd,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
                    print_log('restore {0} successed'.format(db_name))
                except subprocess.CalledProcessError as e:
                    print_log('error found, restore terminated')
except SystemExit:
    print_log('error found, process terminated')
except:
    print_log('{0}: {1}'.format(str(sys.exc_info()[0]),
                                str(sys.exc_info()[1])))
