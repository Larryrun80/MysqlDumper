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
def del_backup(backup_path, backup_dir, time_format, keep_data_period):
    # If found backup dir, do
    if os.path.exists(backup_path + backup_dir):
        # get the start pos of the time string in backup dir name
        date_pos = backup_dir.find(time.strftime(time_format))
        if date_pos == -1:
            print_log("defined dir name is invalid, clean up terminated")
            return
        else:
            # get a valid backuped dirname
            prefix = backup_dir[0:date_pos]
            # for every dir in your backup path
            # check if its too old
            for dirname in os.listdir(backup_path):
                if dirname.find(prefix) == 0:
                    try:
                        end_pos = date_pos+len(time.strftime(time_format))
                        date_str = dirname[date_pos:end_pos]
                        keep_days = datetime.timedelta(days=keep_data_period)
                        created_date = datetime.datetime.strptime(date_str,
                                                                  time_format)
                        if created_date < datetime.datetime.today()-keep_days:
                            # delete backuped dir and files if its old enough
                            del_dir = backup_path + dirname
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

# [GENERAL_SETTINGS]
# Time_Format = %Y%m%d-%H%M%S
# Keep_Data_Period = 7
# PRERESTORE_COMMAND = your cammand

# [RESTORE_SETTINGS]
# Host = localhost
# User = username
# Password = password
# PORT = 3306
# Prefix =

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

# Read README.md to find how to configure this file



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

# Debug mode, if you turns this option to "True", MysqlDumper will print
# backup command and restore command(if there are any dbs to be restored)
DEBUG_MODE = True

# ##############################
# ##### END OF CONFIG PART #####
# ##############################

print('''
#################################################################
============== START BACKUP ON {0} ==============
#################################################################

      '''
      .format(time.strftime('%Y-%m-%d %H:%M:%S')))

try:
    # Checking config file
    config = ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print_log('Config file not found at: {0}, exit'
                  .format(os.path.abspath(CONFIG_FILE)))
        sys.exit()
    config.read(CONFIG_FILE)

    # Loading general settings and init
    legal_config_file = False
    if config.has_section('GENERAL_SETTINGS'):
        if config. has_option('GENERAL_SETTINGS', 'Time_Format')\
           and config. has_option('GENERAL_SETTINGS', 'Keep_Data_Period'):
            time_format = config.get('GENERAL_SETTINGS', 'Time_Format')
            keep_data_period = config.get('GENERAL_SETTINGS',
                                          'Keep_Data_Period')
            legal_config_file = True
            if keep_data_period.isdigit():
                keep_data_period = int(keep_data_period)
            else:
                print_log('Wrong format of Keep_Data_Period: '
                          '{0}'.format(keep_data_period))
                keep_data_period = -1
        pre_restore_command = None
        post_restore_command = None
        if config.has_option('GENERAL_SETTINGS', 'Pre_Restore_Command')\
           and config.get('GENERAL_SETTINGS', 'Pre_Restore_Command') != '':
            pre_restore_command = config.get('GENERAL_SETTINGS',
                                             'Pre_Restore_Command')
        if config.has_option('GENERAL_SETTINGS', 'Post_Restore_Command')\
           and config.get('GENERAL_SETTINGS', 'Post_Restore_Command') != '':
            post_restore_command = config.get('GENERAL_SETTINGS',
                                             'Post_Restore_Command')

    # Define the base backup folder and bake up file name
    # generate real-time backup folder and file using current datetime
    backup_path = os.path.abspath(os.path.dirname(__file__))
    backup_path += '/backup/'
    backup_dirname = 'db-' + time.strftime(time_format)
    today_backup_path = backup_path + backup_dirname

    # Checking if backup folder already exists. Create it if not.
    print_log("checking backup folder")
    if not os.path.exists(today_backup_path):
        os.makedirs(today_backup_path)
        print_log('created backup folder: {0}'.format(today_backup_path))
    else:
        print_log('backup folder found at {0}'.format(today_backup_path))

    # Cleaning former backuped data
    if keep_data_period < -1:
        print_log("wrong format of keep_data_period,"
                  " needs to be int and larger than -1, skip clean data stage")
    elif keep_data_period != -1:
        print_log("start cleaning up data backuped before {0} days"
                  .format(keep_data_period))
        del_backup(backup_path, backup_dirname, time_format, keep_data_period)

    # Geting databases and backup
    for database in config.sections():
        if database != 'RESTORE_SETTINGS' and database != 'GENERAL_SETTINGS':
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
                           + today_backup_path \
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
            if pre_restore_command is not None and pre_restore_command != '':
                try:
                    subprocess.check_call(pre_restore_command,
                                          stderr=subprocess.STDOUT,
                                          shell=True)
                except subprocess.CalledProcessError as e:
                    print_log('error found when execute pre-restore command: \
                               {0}'.format(pre_restore_command))

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
                             + " mysql -f -h"\
                             + config.get('RESTORE_SETTINGS', 'Host') \
                             + " -u" \
                             + config.get('RESTORE_SETTINGS', 'User') \
                             + " " \
                             + backup_name \
                             + " < " \
                             + today_backup_path \
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

                    # Execute any bash commands if needs
                    if post_restore_command is not None\
                       and post_restore_command != '':
                        try:
                            subprocess.check_call(post_restore_command,
                                                  stderr=subprocess.STDOUT,
                                                  shell=True)
                        except subprocess.CalledProcessError as e:
                            print_log('error found when execute post-restore command: \
                                       {0}'.format(post_restore_command))
                except subprocess.CalledProcessError as e:
                    print_log('error found, restore terminated')
except SystemExit:
    print_log('error found, process terminated')
except:
    print_log('{0}: {1}'.format(str(sys.exc_info()[0]),
                                str(sys.exc_info()[1])))
