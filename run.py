#!/usr/bin/env python
import subprocess
import pipes


class MySqlDump:
    def __init__(self):
        self.DB_HOST = 'localhost'
        self.DB_USER = 'root'
        self.DB_USER_PASSWORD = ''
        self.DB_NAME = 'tripian_db'
        self.TO_DB_NAME = 'tripian_tribot'
        self.MYSQL_DUMP_DIR = 'C:/xampp/mysql/bin'
        self.BACKUP_PATH = 'backup'
        self.FILE_NAME_SCHEMA = self.BACKUP_PATH + '/tribot_schema_pack.sql'
        self.FILE_NAME_DATA_PACK = self.BACKUP_PATH + '/tribot_data_pack.sql'

        self.MYSQL_SETTINGS = '-h ' + self.DB_HOST + ' -u ' + self.DB_USER + ' --password=' + self.DB_USER_PASSWORD
        self.DUMP_CODE = self.MYSQL_DUMP_DIR + '/mysqldump ' + self.MYSQL_SETTINGS
        self.DUMP_MYSQL_CODE = self.MYSQL_DUMP_DIR + '/mysql ' + self.MYSQL_SETTINGS

    def step1_create_import(self):

        # Export Sql #

        command_schema = '%s --no-data --skip-triggers %s | sed ‘$!N;s/^\(\s*[^C].*\),\n\s*CONSTRAINT.*FOREIGN KEY.*$/\1/;P;D’ | grep -v ‘FOREIGN KEY’ > %s' % \
                         (self.DUMP_CODE, self.DB_NAME, pipes.quote(self.FILE_NAME_SCHEMA))

        command_data = '%s --no-create-info %s > %s' % \
                       (self.DUMP_CODE, self.DB_NAME, pipes.quote(self.FILE_NAME_DATA_PACK))

        subprocess.Popen(command_schema, shell=True).wait()
        subprocess.Popen(command_data, shell=True).wait()

        # Create Database & Import Sql #

        command_create = '%s -e "CREATE DATABASE IF NOT EXISTS %s";' % (self.DUMP_MYSQL_CODE, self.TO_DB_NAME)
        subprocess.Popen(command_create, shell=True).wait()

        command_use_schema = '%s %s < %s' % (self.DUMP_MYSQL_CODE, self.TO_DB_NAME, self.FILE_NAME_SCHEMA)
        command_use_data = '%s %s < %s' % (self.DUMP_MYSQL_CODE, self.TO_DB_NAME, self.FILE_NAME_DATA_PACK)

        subprocess.Popen(command_use_schema, shell=True).wait()
        subprocess.Popen(command_use_data, shell=True).wait()

        print("step 1 finish")
        self.step2_place_control()

    def step2_place_control(self):

        # Delete type null or blank #
        command_delete_type = '%s -e "DELETE FROM %s.tribot_places WHERE placetype_id is null or placetype_id = \'\' ";' % (self.DUMP_MYSQL_CODE, self.TO_DB_NAME)
        subprocess.Popen(command_delete_type, shell=True).wait()

        # Status 2 replace to 1 #
        command_update = '%s -e "UPDATE %s.tribot_places SET status = 1 WHERE status = 2";' % (self.DUMP_MYSQL_CODE, self.TO_DB_NAME)
        subprocess.Popen(command_update, shell=True).wait()

        # Delete non status 1 #
        command_delete = '%s -e "DELETE FROM %s.tribot_places WHERE status <> 1";' % (self.DUMP_MYSQL_CODE, self.TO_DB_NAME)
        subprocess.Popen(command_delete, shell=True).wait()

        # Delete places_hours not in id place #
        command_delete = '%s -e "DELETE FROM %s.tribot_places WHERE status <> 1";' % (
        self.DUMP_MYSQL_CODE, self.TO_DB_NAME)
        subprocess.Popen(command_delete, shell=True).wait()

        print("step 2 finish")


if __name__ == "__main__":
    move = MySqlDump()
    move.step1_create_import()
