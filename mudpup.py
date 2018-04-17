#Eric Bitikofer
#02.10.17
#This is a python program the scrapes the Ohio University Engineering Department
# faculty directory for first name, last name, and email and transfers those values
# into a database chosen by the user

import sqlite3                                # for database manipulation
import urllib.request                         # for urlopen
import re                                     # for regular expressiosn
import sys                                    # for command line arguments and exit

#connect_database
#   connects to a database passed in as a parameter
#
# parameters:
#   database - a string of the name of a local database
#
# returns:
#   a (database) connection object if the try works, None if it fails
def connect_database(database):
    try:
        database_connection = sqlite3.connect(database)     #create a connection to the database
        return database_connection                          #return that connection
    except Exception as exc:                                #catch exception if try fails
        print(exc)                                          #print the exception
    return None                                             #return None if an exception is caught

#pull_webpage
#   pulls a string of the source code of the webpage passed in as a parameter
#
# parameters:
#   url - a string of the url of the source for scraping
#
# returns:
#   a string of the source code the the page designated by the url
def pull_webpage(url):
    site_connection = urllib.request.urlopen(url)           #open the url
    scan_string = site_connection.read().decode('utf-8')    #read and decode the source code
    return scan_string                                      #return a string of the source code

#deconstruct_string
#   pulls apart the string passed in as a parameter, according to the regex defined
#
# parameters:
#   scan_string - a string of the source for deconstruction
#
# returns:
#   a list of lists (first names, last names, and emails)
def deconstruct_string(scan_string):
                                                            #regex for finding names
    names = re.findall(r"[A-Z]{1}[.A-Za-z-]+\s*[A-Z]*.*\xa0[A-Z]{1}[A-Za-z-]+", scan_string)
                                                            #regex for finding emails
    emails = re.findall(r"(?<=mailto:)[\w._%+-]+@[\w.-]+\.[A-Za-z]{2,4}", scan_string)

    first_names = []                                        #empty list for filling with first names
    last_names = []                                         #empty list for filling with last names
    for name in names:
        full_name = re.split(r"\xa0", name)                 #splits on the nbsp;(\xa0) between names
        first_names.append(full_name[0])                    #appends the first part to first_names
        last_names.append(full_name[1])                     #appends the second part to last_names

    entries = []                                            #empty list for filling with lists
    entries.append(first_names)                             #appends first names list
    entries.append(last_names)                              #appends last names list
    entries.append(emails)                                  #appends emails list
    return entries                                          #returns list of lists

#generate_table
#   creates a cursor and creates a table if it doesn't already exist
#
# parameters:
#   database_connection - a connection object pointing to the database for filling
#   table_sql - a string of the sql command for executing create a database table
#
# returns:
#   nothing
def generate_table(database_connection, table_sql):
    if database_connection is not None:                     #checks database connection
        cur = database_connection.cursor()                  #creates a cursor at database
        cur.execute(table_sql)                              #executes the create table sql cmd
    else:
        print("No database!")                               #tells the user if the database dne

#transfer_entries
#   tranfers entries to the databse table from the lists passed in as a parameter
#
# parameters:
#   entries - a list of lists that include the names and emails needed for poulating the database
#   database_connection - a connection object pointing to the database for filling
#   entry_sql - a string of the sql command for executing to fill a database entry
#
# returns:
#   nothing
def transfer_entries(entries, database_connection, entry_sql):
    first_names = entries[0]                                #set first_names to first list
    last_names = entries[1]                                 #set last_names to second list
    emails = entries[2]                                     #set emails to third list
    for first_name, last_name, email in zip(first_names, last_names, emails):
        with database_connection:
            entry = (first_name, last_name, email)          #creates entry strings
            cur = database_connection.cursor()              #creates a cursor at database
            cur.execute(entry_sql, entry)                   #executes the create entry sql cmd

def main(argv):

    if len(argv) > 1:
        print('Too many arguments')                             #notify user of command syntax error
        print('emailscrape.py <db_name>')                       #print proper format of arguments
        sys.exit()                                              #exit without executing

    with open(argv[0], 'r') as infile:
        inputs = infile.read().splitlines()                     #open the input file into a list

    location = inputs[0]                                        #set database location as argument 1
    url = inputs[1]                                             #url to scan in
                                                                #create table sql command
    table_sql = """ CREATE TABLE IF NOT EXISTS entries(id integer PRIMARY KEY, first text NOT NULL, last text NOT NULL, email text NOT NULL); """
                                                                #insert entry sql command
    entry_sql = ''' INSERT INTO entries(first,last,email) VALUES(?,?,?) '''

    database_connection = connect_database(location)            #return the database connection
    scan_string = pull_webpage(url)                             #return the page source code
    entries = deconstruct_string(scan_string)                   #return the entries in a list
    generate_table(database_connection, table_sql)              #generate the table if necessary
    transfer_entries(entries, database_connection, entry_sql)   #transfer the lists to the table

if __name__ == "__main__":                                      #makes sure main runs
    main(sys.argv[1:])                                          #uses cmdline args as main parameter
