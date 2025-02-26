import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
import os
import hmac


def create_db_connection(host, port, user, password, db_name):
    """
    Establishes and returns a connection object to a MySQL database.

    This function attempts to connect to a MySQL database using the provided
    connection parameters such as host, port, user, password, and database
    name. If the connection is successful, it returns the connection object.
    If the connection fails, it prints the error message and returns None.

    Parameters:
        host (str): The hostname or IP address of the MySQL server.
        port (int): The port number for the MySQL server.
        user (str): The username to use for authentication.
        password (str): The password to use for authentication.
        db_name (str): The name of the database to connect to.

    Returns:
        Connection or None: The MySQL connection object if the connection
        was successful, else None.

    Raises:
        None
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            passwd=password,
            database=db_name,
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection


def execute_query(connection, query):
    """
    Executes a SQL query on a given database connection.

    This function takes a database connection and an SQL query as inputs.
    It executes the given query using the connection's cursor, commits the
    transaction, and prints a success message if the query is successful. If
    an error occurs during execution, it prints the error message and
    returns None. The function ensures the cursor is automatically closed
    after operation.

    Args:
        connection: The database connection object.
        query (str): The SQL query to be executed.

    Returns:
        cursor: The database cursor object after successfully executing
        the query, or None if an error occurs.
    """
    try:
        with connection.cursor(buffered=True) as cursor:
            cursor.execute(query)
            connection.commit()
            print("Query successful")
            return cursor
    except Error as err:
        print(f"Error: '{err}'")
        return None


def read_query(connection, query):
    """
    A helper function to execute a SQL query and fetch all results from a database connection.

    This function takes an active database connection and a specified SQL query, executes the
    query using the provided connection, and returns the results as a list. If an error occurs
    during execution, the function will catch it, print the error message, and return None.

    Parameters:
        connection: The active database connection object used for executing the query.
        query: str
            The SQL query string to be executed against the database.

    Returns:
        list:
            A list containing the results of the executed query. Returns None if an error
            occurs during query execution.
    """
    try:
        with connection.cursor(buffered=True) as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
            connection.commit()
            return result
    except Error as err:
        print(f"Error: '{err}'")
        return None


def get_table_columns(connection, db_name, table):
    """
    Fetches the column names of a specific table in a database.

    The function constructs an SQL query to retrieve all column names from
    the INFORMATION_SCHEMA for a given table in a specific database. It
    then executes the query using the provided database connection to fetch
    the column information.

    Parameters:
        connection (Any): The database connection object used to execute the query.
        db_name (str): The name of the database to query.
        table (str): The name of the table for which column names are to be retrieved.

    Returns:
        list: A list of column names for the specified table, retrieved from
        the database.

    Raises:
        Any exceptions thrown by the `read_query` function.
    """
    column_query = (
        f"SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` "
        f"WHERE `TABLE_SCHEMA`='{db_name}' AND `TABLE_NAME`='{table}';"
    )
    return read_query(connection, column_query)


def get_id_column_name(table):
    """
    Gets the ID column name for a specified table.

    This function maps the provided table name to a corresponding ID column name
    based on a predefined dictionary of mappings. If the given table is not found
    in the mapping, a default ID column name 'ID' will be returned. The function
    handles specific tables such as 'Borrowers', 'Properties', 'MortgageLoans',
    'Payments', 'Guarantor_Cosigners', and 'Insurance'.

    Parameters:
        table (str): Name of the table for which the ID column name is requested.

    Returns:
        str: The ID column name associated with the specified table, or 'ID' if
             the table name is not found in the mapping.
    """
    id_column_mapping = {
        'Borrowers': 'BorrowerID',
        'Properties': 'PropertyID',
        'MortgageLoans': 'LoanID',
        'Payments': 'PaymentID',
        'Guarantor_Cosigners': 'GuarantorID',
        'Insurance': 'LoanID'
    }
    return id_column_mapping.get(table, 'ID')


def create_record(connection, db_name, table):
    """
    Create a new record in the specified database table.

    This function generates a user interface for entering data for a new record in the selected
    database table. It retrieves the table's columns and provides input fields for each column,
    excluding the primary key column, which is auto-generated. Once the user fills in the required
    fields and confirms, the data is inserted into the table.

    Parameters:
        connection (Any): The active database connection object used to execute queries.
        db_name (str): The name of the database containing the target table.
        table (str): The name of the table where the new record will be created.

    Raises:
        No exceptions explicitly raised by this function.

    Returns:
        None
    """
    columns = get_table_columns(connection, db_name, table)
    primary_key = get_id_column_name(table)
    user_input = {}
    for col in columns:
        col_name = col[0]
        if col_name == primary_key:
            st.text_input(f"Primary Key {col_name}", value="Auto-generated", disabled=True)
        else:
            user_input[col_name] = st.text_input(f"Enter {col_name}")
    if st.button("Create Record"):
        column_names = ', '.join(user_input.keys())
        column_values = "', '".join(user_input.values())
        insert_query = f"INSERT INTO {table} ({column_names}) VALUES ('{column_values}');"
        execute_query(connection, insert_query)
        st.success(f"Record created successfully in {table}!")


def read_records(connection, table):
    """
    Fetches all records from a specified database table and displays them in a
    streamlit dataframe.

    This function reads data from the given table by executing a SQL SELECT query,
    converts the data into a pandas DataFrame object for easier manipulation, and
    renders it to a Streamlit app.

    Args:
        connection: A database connection object used to execute the SELECT query.
        table (str): Name of the database table whose records are to be fetched.

    Returns:
        None
    """
    select_query = f"SELECT * FROM {table};"
    records = read_query(connection, select_query)
    with connection.cursor(buffered=True) as cursor:
        cursor.execute(select_query)
        col_names = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(records, columns=col_names)
    df.reset_index(drop=True, inplace=True)
    st.dataframe(df, hide_index=True)


def update_record(connection, db_name, table):
    """
    Updates an existing record in the specified database table based on user interaction.

    This function allows the user to select a record from a database table via a presented dropdown
    and update specific fields. Input fields for editing the values are prepopulated with the
    current data. The primary key of the record cannot be modified. Updates are committed to the
    database upon confirmation by the user.

    Arguments:
        connection (object): A database connection object to interact with the database.
        db_name (str): The name of the database containing the table.
        table (str): The name of the table from which the record is to be updated.

    Returns:
        None: The results are communicated via the Streamlit interface and database updates.
    """
    # Get column info and the primary key column name
    columns = get_table_columns(connection, db_name, table)
    id_col = get_id_column_name(table)

    # Query the list of existing primary key values from the table
    pk_query = f"SELECT {id_col} FROM {table};"
    pk_result = read_query(connection, pk_query)
    primary_keys = sorted([row[0] for row in pk_result] if pk_result else [])

    if not primary_keys:
        st.error("No records found to update.")
        return

    # Use a dropdown to select which record to update
    selected_pk = st.selectbox(f"Select the {id_col} of the record you want to update", primary_keys)

    if selected_pk:
        # Construct the SELECT query using the exact order of columns
        columns_str = ", ".join([col[0] for col in columns])
        record_query = f"SELECT {columns_str} FROM {table} WHERE {id_col}='{selected_pk}';"
        record_result = read_query(connection, record_query)
        if not record_result:
            st.error("Record not found.")
            return

        # Assuming only one record is returned (as primary keys are unique)
        record = record_result[0]
        user_input = {}

        # Loop over all columns to create input fields with the existing values populated
        for idx, col in enumerate(columns):
            col_name = col[0]
            existing_value = record[idx]

            # For the primary key field, simply display the value, no edit allowed
            if col_name == id_col:
                st.write(f"{col_name}: {selected_pk}")
                user_input[col_name] = selected_pk
            else:
                # Prepopulate the text input with the current value of the field
                user_input[col_name] = st.text_input(f"Enter {col_name}", value=str(existing_value))

        if st.button("Update Record"):
            # Build the SET clause excluding the primary key
            set_clause = ', '.join(
                [f"{col}='{value}'" for col, value in user_input.items() if col != id_col]
            )
            update_query = f"UPDATE {table} SET {set_clause} WHERE {id_col}='{selected_pk}';"
            execute_query(connection, update_query)
            st.success(f"Record updated successfully in {table}!")


def delete_record(connection, db_name, table):
    """
    Handles the deletion of a specific record from the specified table and database based on
    user input. Retrieves the record to be deleted and displays it for confirmation before
    deleting. Executes the deletion and provides success feedback to users through an interactive
    interface.

    Args:
        connection: A database connection object used to interact with the database.
        db_name: Name of the database from which the record should be deleted.
                 The type of this parameter follows the type hint in code.
        table: Name of the table from which the record should be deleted.
               The type of this parameter follows the type hint in code.
    """
    id_col = get_id_column_name(table)
    st.write(f"Enter the {id_col} of the record you want to delete")

    select_ids_query = f"SELECT {id_col} FROM {db_name}.{table};"
    records = read_query(connection, select_ids_query)
    record_ids = sorted([record[0] for record in records])
    selected_record = st.selectbox(f"Select {id_col} to delete", record_ids)
    active_record_query = f"SELECT * FROM {db_name}.{table} WHERE {id_col}={int(selected_record)};"
    with connection.cursor() as cursor:
        cursor.execute(active_record_query)
        active_record = cursor.fetchone()
        col_names = [desc[0] for desc in cursor.description]
    active_record_df = pd.DataFrame([active_record], columns=col_names)

    st.markdown("**Record to be deleted:**")
    st.dataframe(active_record_df, hide_index=True)
    delete_query = f"DELETE FROM {db_name}.{table} WHERE {id_col}={int(selected_record)};"
    if st.button("Delete Record"):
        with connection.cursor() as cursor:
            cursor.execute(delete_query)
            connection.commit()
        st.success(f"Record deleted successfully from {table}!")


def check_password():
    """
    Check if the entered password matches the secret password using an HMAC-based
    comparison for security. Manage the state of password correctness through the
    Streamlit session state. This function uses Streamlit widgets for password entry
    and error reporting.

    Parameters:
        None

    Raises:
        None

    Returns:
        bool: True if the entered password matches the secret password, False otherwise.
    """

    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


def main():
    st.set_page_config(page_title="Mortgage Management System",
                       layout="wide",
                       initial_sidebar_state="expanded")
    st.title("Mortgage Management System")
    host = os.getenv("MYSQL_HOST")
    port = int(os.getenv("MYSQL_PORT"))
    user = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    db_name = os.getenv("MYSQL_DATABASE")

    db_connection = create_db_connection(host, port, user, password, db_name)

    menu = st.sidebar.selectbox(
        "Choose option:",
        ("Home", "Create record", "Read record", "Update record", "Delete record"),
    )
    table_selected = st.sidebar.selectbox(
        "Choose a table",
        ('Borrowers', 'Properties', 'MortgageLoans', 'Payments', 'Guarantor_Cosigners', 'Insurance')
    )

    if menu == "Home":
        st.header("Welcome to The *Mortgage Management System*")

    elif menu == "Create record":
        st.header("Create a new record on table " + table_selected)
        create_record(db_connection, db_name, table_selected)

    elif menu == "Read record":
        st.header("Read a record from table " + table_selected)
        read_records(db_connection, table_selected)

    elif menu == "Update record":
        st.header(f"Update a record from {table_selected} table")
        update_record(db_connection, db_name, table_selected)

    elif menu == "Delete record":
        st.header(f"Delete a record from {table_selected} table")
        delete_record(db_connection, db_name, table_selected)


if __name__ == "__main__":
    if not check_password():
        st.stop()
    else:
        main()
