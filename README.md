# MysqlDumper
Scripts help you backup/restore your database, support mysql 5.x  
Support ignore table, connect to remote db via ssh tunnel  
Support just keep recent backup files to release your disk capacity  
You should have a Python 3.x enviroment to run MysqlDumper  

## Installation
Check our MysqlDumper where you want to install it. Went to some suitable place and run:
```
$ git clone https://github.com/Larryrun80/MysqlDumper.git
```

## Upgrading
To upgrade to the latest version of MysqlDumper, use git pull:
```
$ cd <your MysqlDumper dir>
$ git pull
```

## Uninstalling
Delete your MysqlDumper directory.

## How to use
1. You can run MysqlDumper manually
```
$ python mysqldumper.py
```
2. You can add mysqldumper to your crontab list
If you are using crontab to run MysqlDumper, you can use "> some_log_file" to record MysqlDumper outputs.
Be aware of enviroment variable when you are using crontab.
We suggest you using [pyenv](https://github.com/yyuu/pyenv) or virtualenv to manage your python versions.

## Create config files
- You can simply mv mysqldumper.conf.sample to mysqldumper.conf and fill your databases settings
- You can also create conf file manually, if you want do this:
create a config file with following format to run MysqlDumper correctly:
```
[RESTORE_SETTINGS]
Host = localhost
User = username
Password = password
Port = 3306
Prefix = backupd

[DATABASE_NAME_TO_BACKUP]
Host = host
User = username
Password = password
Database = database
Port = 3306
Ignore_Tables = table_a,
                table_b,
                table_c
Need_Restore = yes
SSH_Tunnel = username@host
```

First part [RESTORE_SETTINGS] is used for restore operations
If you only want to backup a db but do not need it restored, skip it.
But if you want to use this section, be care keep it name as "RESTORE_SETTINGS".

Second part [DATABASE_NAME_TO_BACKUP] is used for backup operations, you can create multi sections with same format to backup multi databases, you can change section name to everything you need, but we suggest you use your database name.
In this part, make sense "Need_Restore" option indicate if this database should be restored after backuped, use "yes" or "no" as its value.
You can pass SSH_Tunnel option if you do not need to connect database using SSH Tunnel. If you want to use this function, pls make sense it's now only support ssh key tunnels. Read [this](https://wiki.archlinux.org/index.php/SSH_keys#Generating_an_SSH_key_pair) if you want to know how to use SSH Keys.

You can create this config file as conf/mysqldumper.conf
Or change the default config file in mysqldumper.py

## Customization
You can do some customization job to fit your requirements， of course you can also skip this part, MysqlDumper will work correctly, too.
Now we list some customization options below, you can find them in mysqldumper.py and change its value:
- CONFIG_FILE  
    You can set your own config file location and config file name here
- TIME_FORMAT  
    Time format is used to organize your favirate backup file name. If you want to change it, remember to rewrite it in python's strftime format, but we suggest you keep year(%Y), month(%m), date(%d) information, especially if you want to restore a db after its backuped.
- BACKUP_PATH  
    You can define where to put your backup files
- BACKUP_DIRNAME  
    In BACKUP_PATH, we will create a backup directory every time you run this program, you can specify your personal backup dir name here, but remember to include "time.strftime(TIME_FORMAT)", this will import your favirate time format to be a part of your dir name, of you can also just use "time.strftime(TIME_FORMAT)" as your dir name.
- KEEP_DATA_PERIOD  
    Set days you want to keep your backup data. Default value is to keep recent 7 days' data. This option is very important if you run this program automaticly using crontab or something else. Set the value to "-1" if you want to keep all backuped data. 

## Dealing Errors
The script always tries to give out detail error info, if you found obstacle to get error info, please inform me.
When you are backing up a large db, lots errors may be caused by you mysql settings, like:
- MSQL0003: MySQL backup operation fails with lost connection error
which with information:
```
Backup fail with: Mysqldump: Error 2013: Lost connection to MySQL server during query when dumping table.
```
if you encounter this error when backing up your db, try to:
1. set the value for "max_allowed_packet" variable as 1GB in your my.cnf
2. increase the value for the "connect_timeout" variable to 100
and restart your mysql.

- 2006: MySQL server has gone away
```
ERROR 2006 (HY000) at line xxx: MySQL server has gone away
```
if you encounter this error when restoring your db, try to:
1. set the value for "max_allowed_packet" variable as 1GB in your my.cnf
2. increase the value for the "wait_timeout" variable to 6000
and restart your mysql.

## Todo
- Add more mysqldump parameters if needed
