#!/usr/bin/env python3
import mysql.connector as m
from os.path import join
from db_config import CONFIG
import time

def connect():
    cxn = m.connect(
        host=CONFIG['host'],
        user=CONFIG['user'],
        passwd=CONFIG['password']
    )
    return cxn

def get_databases(cxn):
    """
    Args:
        cxn: the MySQL database connection object
    Returns:
        a tuple of strings of database names
    """
    cursor = cxn.cursor()
    cursor.execute('SHOW DATABASES')
    # cursor.fetchall() returns a list of singleton tuples
    tups = cursor.fetchall()
    cursor.close()
    return [x[0] for x in tups]


def get_tables(cxn, database_name):
    """
    Args:
        cxn: the MySQL database connection object
        database_name: the name of the database to get tables from
    Returns:
        a tuple of strings of database names
    """
    acceptable_list = ['dev']
    assert database_name in acceptable_list, "unexpected database_name"

    cursor = cxn.cursor()
    cursor.execute('use ' + database_name)
    cursor.execute('show tables')
    # cursor.fetchall() returns a list of singleton tuples
    tups = cursor.fetchall()
    cursor.close()
    return [x[0] for x in tups]


def run_create_script(cxn, filename):
    """
    Args:
        cxn: the MySQL database connection object
    Returns:
        True if succeeded
    """
    c = cxn.cursor()
    with open(filename, 'r') as f:
        c.execute(f.read())
    time.sleep(2)
    c.close()
    return True

 
if __name__ == "__main__":
    cxn = connect()

    print("getting databases...", get_databases(cxn))
    print("getting tables...", get_tables(cxn, 'dev'))

    script = join(CONFIG['sql_dir'], CONFIG['create_file'])

    print("running create script...")
    assert run_create_script(cxn, script) == True, "uh oh failed to create"

    cxn.close()
    cxn = connect()

    print("getting tables...", get_tables(cxn, 'dev'))

    cxn.close()