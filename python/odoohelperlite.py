#!/usr/bin/env python3
'''
Smaller standalone miniclient to query the Odoo installation for data.

(Got bogged down with getting outils-helper act nicely with Zabbix)

TODO: Rewrite this to use outils instead.

The entire script is intended to run as the Odoo user.
'''

import getpass
import json
import os
import subprocess

import click
import psycopg2

#%% Definitions
ODOOUSER = "odoo"
ODOO_FILESTORE = "/var/lib/odoo/.local/share/Odoo/filestore"

#%% Tools
# Templates and query from Odoo 14
TEMPLATES = "('template0','template1','postgres')"
SQL_LIST_DATABASES = f"select datname from pg_database where datdba=(select usesysid from pg_user where usename=current_user) and not datistemplate and datallowconn and datname not in {TEMPLATES} order by datname"
def odoo_db_list():
    '''Connect to db 'postgres' and return list of  Odoo dbs'''
    conn = psycopg2.connect(database="postgres")
    with conn.cursor() as c:
        c.execute(SQL_LIST_DATABASES)
        result = [r[0] for r in c.fetchall()]
    conn.close()
    return result

SQL_SYSTEM_PARAM = "SELECT value FROM ir_config_parameter WHERE key='{}';"
def odoo_get_system_param(database,parameter):
    '''
    Get system parameter
    '''
    conn = psycopg2.connect(database=database)
    with conn.cursor() as c:
        c.execute(SQL_SYSTEM_PARAM.format(parameter))
        result = c.fetchall()[0][0]
    conn.close()
    return result

SQL_BASE_URL = "SELECT value FROM ir_config_parameter WHERE key='web.base.url';"
SQL_BASE_URL_FREEZE = "SELECT value FROM ir_config_parameter WHERE key='web.base.url.freeze';"
def odoo_get_base_url(database):
    '''
    '''
    conn = psycopg2.connect(database=database)
    with conn.cursor() as c:
        c.execute(SQL_BASE_URL)
        result = c.fetchall()[0][0]
    conn.close()
    return result

def odoo_get_base_url_freeze(database):
    '''
    '''
    conn = psycopg2.connect(database=database)
    with conn.cursor() as c:
        c.execute(SQL_BASE_URL_FREEZE)
        result = boolean(c.fetchall()[0][0])
    conn.close()
    return result

SQL_DB_SIZE_BYTES_FORMAT = "SELECT pg_database_size('{}')"
def odoo_get_db_size(database):
    '''Get database size in bytes.'''
    conn = psycopg2.connect(database=database)
    with conn.cursor() as c:
        c.execute(SQL_DB_SIZE_BYTES_FORMAT.format(database))
        result = int(c.fetchall()[0][0])
    conn.close()
    return result

def odoo_get_db_sizes_total():
    '''
    Total size of the Odoo databases.
    '''
    dbs = odoo_db_list()
    return sum( ( odoo_get_db_size(db) for db in dbs ) )


def odoo_get_db_filestore_sizes(basedir=ODOO_FILESTORE):
    '''
    Get a db -> size dict mapping name to filestore size in bytes.
    '''
    # du -bd 1 <->  list size of filetree in bytes recurively to depth 1
    result_raw = subprocess.run(["du","-b","-d","1",basedir],
                                capture_output=True).stdout.decode("utf-8")
    ret = {}
    for row in result_raw.split("\n"):
        if not row:
            continue
        column = row.split()
        if len(column) != 2:
            continue
        s = int(column[0])
        f_raw = column[1]
        # Special case
        if f_raw == basedir:
            ret["all"] = s
        else:
            ret[os.path.basename(f_raw)] = s
    return ret

def odoo_get_db_filestore_size(database, basedir=ODOO_FILESTORE):
    '''
    Get a database's filestore size.
    '''
    return odoo_get_db_filestore_sizes(basedir=basedir)[database]
def odoo_get_db_filestore_size_total(basedir=ODOO_FILESTORE):
    '''
    Get a database's filestore size.
    '''
    return odoo_get_db_filestore_sizes(basedir=basedir)["all"]

def prerun_checks(checkuser=True):
    '''
    Sanity checks to run before the actual operations.
    '''
    if checkuser:
        if not ODOOUSER == getpass.getuser():
            click.echo(f"Test failed. Current user: {getpass.getuser()}. Expected: {ODOOUSER}",err=True)
            return False
    return True

DBMACRO="{#ODOODBNAME}"
def dblist2zabbixjson(dblist):
    '''
    Convert the DB-list to a Zabbix compatible discovery JSON.
    '''
    prejson = [ {DBMACRO: db} for db in dblist ]
    return json.dumps(prejson)


#%% Client
@click.group()
@click.option("-u","--user", help="Dev. Option: Set odoo user.",default=ODOOUSER) # Mainly for test purposes.
@click.option("-f","--filestore", help="Dev. Option: Set filestore.",default=ODOO_FILESTORE) # Mainly for test purposes.
@click.option("--sanity/--no-sanity","sanity", help="Dev. Option: Ignore sanity checks.",default=True) # Mainly for test purposes.
#@click.option("-z","--zabbix",help="Format output as a Zabbix compatible JSON",is_flag=True)
@click.pass_context
def main(ctx, **kwargs):
    '''
    '''
    if kwargs["sanity"] and not prerun_checks():
        click.echo("Prerun checks failed. Are you running as the Odoo user? Exiting ...", err=True)
        exit(1)

    ctx.ensure_object(dict) # As recommended by doc : https://click.palletsprojects.com/en/8.0.x/commands/#nested-handling-and-contexts
    #click.echo(kwargs)
#    if kwargs["ot_handle"]:
#        raise NotImplementedError("Not implemented")
    if kwargs["user"]:
        ctx.obj["user"] = kwargs["user"]
        ODOOUSER = kwargs["user"]
    if kwargs["filestore"]:
        ctx.obj["filestore"] = kwargs["filestore"]
        ODOO_FILESTORE = kwargs["filestore"]



@main.command(help="Display database information.")
@click.option('-l','--list',help="List all Odoo databases.",is_flag=True)
@click.option('-n','--nbr',"--count","count",help="Count all Odoo databases.",is_flag=True)
@click.option('-d','--database',help="Perform operations on the given database.")
@click.option('--db-size',help="Size of db in bytes.",is_flag=True)
@click.option('--fs-size',help="Size of filestore in bytes.",is_flag=True)
@click.option('--size',help="Size of db and filestore in bytes.",is_flag=True)
@click.option('--get-param',help="Get database parameter.",is_flag=True) # TODO: Test and tidy up.
@click.option('--url',help="Get database web.base.url.",is_flag=True) # Todo refactor this option to some get_param option?
@click.option('--url-freeze',help="Get web.base.url.freeze parameter.",is_flag=True)
@click.pass_obj # Enough to get ctx.obj
def database(cobj,**kwargs):
    #click.echo(kwargs)
    # Test database agnostic options first.
    if not kwargs["database"]:
        fs = cobj["filestore"]
        if kwargs["list"]:
            for l in odoo_db_list():
                print(l)
        if kwargs["count"]:
            print(len(odoo_db_list()))
        if kwargs["fs_size"]:
            print(odoo_get_db_filestore_size_total(basedir=fs))
        if kwargs["db_size"]:
            print(odoo_get_db_sizes_total())
        if kwargs["size"]:
            dbs_size = odoo_get_db_sizes_total()
            fss_size = odoo_get_db_filestore_size_total(basedir=fs)
            print(dbs_size+fss_size)
    else:
        db = kwargs["database"]
        fs = cobj["filestore"]
        if kwargs["fs_size"]:
            print(odoo_get_db_filestore_size(db,basedir=fs))
        if kwargs["db_size"]:
            print(odoo_get_db_size(db))
        if kwargs["size"]:
            db_size = odoo_get_db_size(db)
            fs_size = odoo_get_db_filestore_size(db,basedir=fs)
            print(db_size+fs_size)
        if kwargs["url"]:
            print(odoo_get_base_url(db))
        if kwargs["url_freeze"]:
            odoo_get_base_url_freeze(db)

@main.command(help="Run Zabbix Discovery")
def discovery():
    print(dblist2zabbixjson(odoo_db_list()))
#%%
if __name__ == '__main__':
    main(obj={})
