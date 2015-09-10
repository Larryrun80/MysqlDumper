# MysqlDumper
Scripts help you backup/restore your database, support mysql 5.x  
- Support ignore table in backup process  
- Support connecting to remote db via ssh tunnel  
- Support just keeping recent backup files to release your disk capacity  

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
[GENERAL_SETTINGS]
Time_Format = %Y%m%d-%H%M%S
Keep_Data_Period = 7
PRERESTORE_COMMAND = your cammand

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

###### [GENERAL_SETTINGS] 
This part is used for...  general settings.
Keep its name as "GENERAL_SETTINGS"
- Time_Format
    You can define your favorite time format here, it needs to obey python's strftime format. 

    This string will be used in backup directory name. 

    We suggest you use all of "year", "month", "date" info at least, especially if you'd like to let program delete overdue backuped data.

- Keep_Data_Period
    Define the period the program will keep backup data. 

    MysqlDumper will delete backuped data before this date, keep this paramater as -1 if you do not want to delete any backuped data. 

    Make sense that you must have a date information is your backup directory

- Pre_Restore_Command
    You can design some bash command to exec before restore. 

    This command will not be executed if you won't restore any database. 
    
    You can use "&&" if you want to execute multi commands. 
    
    Make sure the command will be operate correctly in bash. 
    
    Keep it '' if you do not need execute anything

###### [RESTORE_SETTINGS]
This part is used for restore operations. 

If you only want to backup a db but do not need it restored, skip it.

If you want to use this section, be care keep its name as "RESTORE_SETTINGS".

###### [DATABASE_NAME_TO_BACKUP] 
This part is used for backup operations, you can create multi sections with same format to backup multi databases, you can change section name to everything you need, but we suggest you use your database name.
PORT, Ignore_Tables, SSH_Tunnel is not a must required config
- Need_Restore
    if you want to restore database after it is backuped, set Need_Restore as 'yes', else keep it 'no'. Remember to add restore settings below if you choose yes
- Ignore_Tables
    If you want to ignore some tables in backup progress, use ',' to seperate them
- SSH_Tunnel
    You can pass SSH_Tunnel option if you do not need to connect database using SSH Tunnel. Write a "username@host_ip" format string to enable it. If you want to use this function, pls make sense it's now only support ssh key tunnels. Read [this](https://wiki.archlinux.org/index.php/SSH_keys#Generating_an_SSH_key_pair) if you want to know how to use SSH Keys.

Make sure you assigned accounts with enough proviliegesleges


You can create this config file as conf/mysqldumper.conf or change the default config file in mysqldumper.py

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

## Debug
If you have encounter some error when backuping and restoring, or you modified some code which generate backup/restore command, you can set option DEBUG_MODE to True. Then the to-be-execute command will be printed.
```
DEBUG_MODE = True
```

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

if you passed this error after setting these parameters but encounter it again later, you can try execute restart restore mysql before restore a database. See Pre_Restore_Command part in config file settings.

## Todo
- Add more mysqldump parameters if needed
