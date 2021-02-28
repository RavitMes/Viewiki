"""
This module handles the creation and management of the database:
     - creates new database if not exits
     - inserts data to database
 """
import logging
import re

import mysql.connector as mysql
from config import DB_NAME, DB_HOST, DB_USER, DB_PASSWD, TABLES
import pandas as pd
from datetime import datetime


def find_term(k, v):
    if v:
        return k
    else:
        return ""


class DB:
    def __init__(self, name=DB_NAME):
        self.name = name
        self.logger = logging.getLogger(__name__)

    def connect(self):
        try:
            self.logger.info("connecting")
            db = mysql.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASSWD)
            cursor = db.cursor()
            return db, cursor
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")


    def create_db(self, tables=TABLES):
        """ Creates database and tables if not exists """
        self.logger.info("Create db and tables if not exists")
        db, cursor = self.connect()
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.name}")
            self.logger.info("db created successfully")
            for table_dict in tables:
                self.add_table(table_dict)
        except mysql.Error as err:
            cursor.close()
            db.close()
            self.logger.error(f'Failed creating database: {err}"')
            raise Exception('DB error')
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def add_table(self, table_dict):
        # create tables
        self.logger.info("adding table")
        db, cursor = self.connect()
        cursor.execute(f"USE {self.name}")
        table_name = list(table_dict.keys())[0]
        info_dict = list(table_dict.values())[0]
        try:
            query_base = f"CREATE TABLE IF NOT EXISTS {table_name} "
            query_content = '( '
            query_content_end = ""
            for col_name, info_col in info_dict.items():
                if col_name != "FOREIGN_KEY" and col_name != "ADD":
                    query_content += f" {col_name} {info_col['TYPE']} "
                    query_content += ' '.join(
                        [find_term(k, v) for k, v in info_col.items() if k != 'TYPE'] + [",\n"])
                else:
                    if col_name == "FOREIGN KEY":
                        query_content_end=''
                        for i in range(len(info_col['col_from'])):
                            query_content_end += f" FOREIGN KEY ({info_col['col_from'][i]}) REFERENCES \
                                                {info_col['table'][i]} ({info_col['col_to'][i]})  " +",\n"
                    elif col_name == "ADD":
                        query_content_end += info_col +",\n"

            total_query = (query_base + query_content + query_content_end).strip(" ,\n")  + " )"
            cursor.execute(total_query)

        except mysql.Error as err:
            self.logger.error(f'Failed creating table: {err}"')
            raise Exception('DB error')
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")
        finally:
            cursor.close()
            db.close()


    def add_user(self, user_obj):
        """ Insert personal information of the user to the table in the database
        """
        self.logger.info("Starting to insert data into db")
        db, cursor = self.connect()
        try:
            cursor.execute(f"USE {self.name}")
            insert_query = '''INSERT IGNORE INTO USERS (NAME, EMAIL, PASSWORD) \
                                VALUES (%s, %s, %s)'''
            record_values = (user_obj.name, user_obj.email, user_obj.password)
            cursor.execute(insert_query, record_values)
            self.logger.info("user added")
            db.commit()
        except mysql.Error as err:
            self.logger.error(f'Failed creating table: {err}"')
            raise Exception('DB error')
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")
        finally:
            cursor.close()
            db.close()


    def extract_user_details(self, password, email):
        self.logger.info(f'extracting details for the user with the email {email}')
        try:
            db, cursor = self.connect()
            cursor.execute(f"USE {DB_NAME}")
            cursor.execute(
                """SELECT * FROM USERS where PASSWORD = '%s' and EMAIL ='%s'""" % (password, email))
            record = cursor.fetchall()
            users = pd.DataFrame(record)
            return users
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def is_record_exist(self, password, email):
        self.logger.info(f'check if the user with the email {email} exists according to his email and password')
        try:
            record = self.extract_user_details(password, email)
            record_num = record.shape[0]
            self.logger.info(f"number of records matching the given fields is:  {record_num}")
            if record_num > 0:
                return True
            return False
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def add_project(self, email, filename):
        """
        """
        self.logger.info(f"Starting to insert project data for the user with the email {email} into db")
        try:
            db, cursor = self.connect()
            #if first time uploading the file - updating projects
            cursor.execute(f"USE {self.name}")
            insert_query = '''INSERT IGNORE INTO PROJECTS (NAME) VALUES (%s)'''
            project_name = re.findall('(.*).csv',filename)[0]
            record_values = (project_name,)
            cursor.execute(insert_query, record_values)
            db.commit()

            #update the log table
            cursor.execute(f"USE {self.name}")
            insert_query = '''INSERT IGNORE INTO LOG (DATE, PROJECT_ID, USER_ID, ACTION) \
                                VALUES (%s, %s, %s, %s)'''
            date = datetime.today().strftime('%Y-%m-%d')
            project_id = int(self.get_project_id(project_name))
            user_id = int(self.get_user_id(email))
            action = 'new_file'
            record_values = (date, project_id, user_id, action)
            cursor.execute(insert_query, record_values)
            db.commit()

            #if first time uploading the file - updating users_projects
            cursor.execute(f"USE {self.name}")
            insert_query = '''INSERT IGNORE INTO USERS_PROJECTS (USER_ID, PROJECT_ID) VALUES (%s, %s)'''
            record_values = (user_id, project_id)
            cursor.execute(insert_query, record_values)
            db.commit()

            #delete the previous rows associated with the project
            cursor.execute("""DELETE FROM WIKI_DATA WHERE PROJECT_ID ='%s' """ % project_id)

            #update the wiki_data table
            insert_query = '''INSERT IGNORE INTO WIKI_DATA (PROJECT_ID, CATEGORY, WIKI_PAGE_URL, PAGE_INTERLINK) \
                                VALUES (%s, %s, %s, %s)'''
            df = pd.read_csv(filename)
            for idx,record in df.iterrows():
                self.logger.info(record)
                d = {"CATEGORY":record["CATEGORY"], "WIKI_PAGE_URL":record["WIKI_PAGE_URL"], "PAGE_INTERLINK":record["PAGE_INTERLINK"]}
                record_values = (project_id, d['CATEGORY'], d['WIKI_PAGE_URL'], str(d['PAGE_INTERLINK']))
                cursor.execute(insert_query, record_values)
            self.logger.info("user added")
            db.commit()
        except mysql.Error as err:
            self.logger.error(f'Failed creating table: {err}"')
            raise Exception('DB error')
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")
        finally:
            cursor.close()
            db.close()


    def get_associated_projects(self, email):
        try:
            self.logger.info(f"get associated projects to {email}")
            db, cursor = self.connect()
            cursor.execute(f"USE {DB_NAME}")
            cursor.execute(
                """SELECT * FROM PROJECTS \
                INNER JOIN USERS_PROJECTS ON PROJECTS.PROJECT_ID = USERS_PROJECTS.PROJECT_ID \
                INNER JOIN USERS ON USERS_PROJECTS.USER_ID = USERS.USER_ID \
                where USERS.EMAIL = '%s' """ % email)
            try:
                record = list(pd.DataFrame(cursor.fetchall())[1])
                return record
            except:
                self.logger.info("no associated projects were found")
                return
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")


    def get_project_id(self, project_name):
        try:
            self.logger.info(f"finding the project ID of the project_name {project_name}")
            db, cursor = self.connect()
            cursor.execute(f"USE {DB_NAME}")
            cursor.execute(
                """SELECT PROJECT_ID FROM PROJECTS where NAME = '%s' """ % project_name)
            record = pd.DataFrame(cursor.fetchall()).values[0]
            return record
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")


    def get_user_id(self, email):
        self.logger.info(f"get user id for the user with the email {email}")
        try:
            db, cursor = self.connect()
            cursor.execute(f"USE {DB_NAME}")
            cursor.execute("""SELECT USER_ID FROM USERS where EMAIL ='%s' """ % email)
            record = pd.DataFrame(cursor.fetchall()).values[0][0]
            return record
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")

    def get_df_from_wiki_data(self, project_name):
        self.logger.info(f"get df from wiki_data table for the project {project_name}")
        try:
            db, cursor = self.connect()
            project_id = self.get_project_id(project_name)
            cursor.execute(f"USE {DB_NAME}")
            record = pd.read_sql(
                """SELECT * FROM WIKI_DATA where PROJECT_ID =%d """ % project_id,
                db)
            return record
        except Exception as err:
            self.logger.info(f"encounter error: {str(err), err.args}")
