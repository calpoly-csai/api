#!/usr/bin/env python3
import mysql.connector as m
from os.path import join
from db_config_sample import CONFIG
import time


def connect():
    cxn = m.connect(host=CONFIG['host'],
                    user=CONFIG['user'],
                    passwd=CONFIG['password'])
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


def what_courses_can_i_take(cxn):
    """Answers the ultimate question of the meaning of life the universe and everything
    which so happens to be the same as "What courses Cal Poly offers"

    Args:
        cxn: the MySQL database connection object
    Returns:
        A list of course names that Cal Poly offers
    """
    c = cxn.cursor()

    c.execute("use dev")  # TODO: make this modular
    c.execute("SELECT courseName FROM Courses")
    # TODO: actually return False error

    tups = c.fetchall()

    # close the cursor
    c.close()

    return [x[0] for x in tups]


def courses_offered(cxn, course):
    """ Answers the question of when can I take "X"course?

    Args:
        cxn: MySQL database connection object
        course: the course user wants terms from. Expected format is string
        "department courseNum"
    Returns:
        A list including courseName and a set of terms offered for specified course
    """
    c = cxn.cursor()

    c.execute("use dev")

    query = "SELECT courseName, termsOffered from Courses where courseName like \"%"
    query += course + "%\""

    print(query)
    c.execute(query)
    tups = c.fetchall()

    c.close()

    return tups


def does_professor_teach_course(cxn, profLastName, profFirstName, course):
    """ Answers the question of 'Does [Professor] teach [Course]'?

    Args:
        cxn: MySQL database connection object
        prof: the name of the professor. If first and last name expressed, otherwise, last name
        will be used alone
        course: the course user wants terms from. Expected format is string
        "department courseNum"
    Returns:
        A boolean
    """
    c = cxn.cursor()

    c.execute("use dev")

    query = "SELECT c.courseName from Courses c INNER JOIN Professors p on c.Professors_id = p.id where p.lastName like \"%"
    query += profLastName + "%\""

    # this can be an article of discussion for matching professor names
    if profFirstName != "":
        query += " and p.firstName likel \"%"
        query += profFirstName + "%\""

    query += " and courseName like \"%"
    query += course + "%\""

    print(query)
    c.execute(query)
    tups = c.fetchall()

    c.close()
    if len(tups) == 0:
        return False
    return True


if __name__ == "__main__":
    cxn = connect()

    print("getting databases...", get_databases(cxn))
    print("getting tables...", get_tables(cxn, 'dev'))

    script = join(CONFIG['sql_dir'], CONFIG['create_file'])

    # print("running create script...")
    # assert run_create_script(cxn, script) == True, "uh oh failed to create"

    cxn.close()
    cxn = connect()

    print("getting tables...", get_tables(cxn, 'dev'))

    print(courses_offered(cxn, "CSC 357"))

    print(does_professor_teach_course(cxn, "Kearns", "", "CSC 349"))

    cxn.close()
