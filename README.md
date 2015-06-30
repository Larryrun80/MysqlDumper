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
