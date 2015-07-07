# MysqlDumper
scripts help you backup/restore your database 

## Create config files
You must have a config file with following format to run mysqldumper correctly:
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
You can create this config file as conf/mysqldumper.conf
Or change the default config file in mysqldumper.py

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
- user can determine whether to delete back up files some date before
