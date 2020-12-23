
import shutil
import toydb as tdb


def test_create_db():
    # Create a new database
    db = tdb.Database("tmp.tdb")
    # Delete the db file
    db.remove()


def test_read_db():
    # Create a new database
    db = tdb.Database("tmp.tdb")
    # Read the database
    db = tdb.Database("tmp.tdb")
    # Clean up
    db.remove()


def test_create_table():
    # Create a new database
    db = tdb.Database("tmp.tdb")
    # Create a table
    table_name = "test_table"
    schema = {
        "some_text": tdb.dtypes.STRING[50],
        "a_number": tdb.dtypes.I32,
        "boolean_val": tdb.dtypes.BOOL,
    }
    db.createTable(table_name,schema)
    assert db.listTables() == [table_name]
    # Delete the db file
    db.remove()

def test_table_rw():
    # Create a new database
    db = tdb.Database("tmp.tdb")
    # Create a table
    table_name = "test_table"
    schema = {
        "some_text": tdb.dtypes.STRING[50],
        "a_number": tdb.dtypes.I32,
        "boolean_val": tdb.dtypes.BOOL,
    }
    db.createTable(table_name,schema)
    # Write data to a table
    data = [
        ("text",42,True),
        (None,256,False),
        ("42",0,None),
    ]
    db.insertMany(table_name,data)
    assert db.query(table_name) == data
    # Delete the db file
    db.remove()

def test_table_query():
    # Create a new database
    db = tdb.Database("tmp.tdb")
    # Create a table
    table_name = "test_table"
    schema = {
        "some_text": tdb.dtypes.STRING[50],
        "a_number": tdb.dtypes.I32,
        "boolean_val": tdb.dtypes.BOOL,
    }
    db.createTable(table_name,schema)
    # Write data to a table
    data = [
        ("text",42,True),
        (None,256,False),
        ("42",0,None)]
    db.insertMany(table_name,data)
    # Test SELECT
    assert db.query(
        table_name,
        select=["some_text"]
    ) == [(r[0],) for r in data]
    # Test WHERE
    assert db.query(
        table_name,
        where=lambda r: None not in r.values()
    ) == [data[0]]
    db.remove()
