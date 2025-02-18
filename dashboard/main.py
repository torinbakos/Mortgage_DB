import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
import os

def create_db_connection(host_name, port, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            port=port,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")
    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
        result = cursor.rowcount
    except Error as err:
        print(f"Error: '{err}'")
        result = None
    return result


def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

def create_record(connection, db_name, table):
    column_query = f"SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='{db_name}' AND `TABLE_NAME`='{table}';"
    columns = read_query(connection, column_query)
    user_input = {}
    for column in columns:
        user_input[column[0]] = st.text_input(f"Enter {column[0]}")

    if st.button("Create Record"):
        column_names = ', '.join(user_input.keys())
        column_values = "', '".join(user_input.values())
        insert_query = f"INSERT INTO {table} ({column_names}) VALUES ('{column_values}');"
        execute_query(connection, insert_query)
        st.success(f"Record created successfully in {table}!")

def read_records(connection, table):
    select_query = f"SELECT * FROM {table};"
    records = read_query(connection, select_query)

    # Extract column names from the database
    cursor = connection.cursor()
    cursor.execute(select_query)
    columns = [desc[0] for desc in cursor.description]

    # Create DataFrame with column names
    df = pd.DataFrame(records, columns=columns)
    df.reset_index(drop=True, inplace=True)

    # Display the DataFrame in Streamlit
    st.dataframe(df)
    return df

def update_record(connection, db_name, table):
    column_query = f"SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='{db_name}' AND `TABLE_NAME`='{table}';"
    columns = read_query(connection, column_query)

    if table == 'Borrowers':
        id_column_name = 'BorrowerID'
    elif table == 'Properties':
        id_column_name = 'PropertyID'
    elif table == 'MortgageLoans':
        id_column_name = 'LoanID'
    elif table == 'Payments':
        id_column_name = 'PaymentID'
    elif table == 'Guarantor_Cosigners':
        id_column_name = 'GuarantorID'
    elif table == 'Insurance':
        id_column_name = 'LoanID'
    else:
        st.error('Unknown table selected')  # Fallback
        id_column_name = 'ID'

    st.write(f'Enter the {id_column_name} of the record you want to update. Other fields will take the new values.')
    user_input = {}
    for column in columns:
        user_input[column[0]] = st.text_input(f"Enter {column[0]}")

    if st.button("Update Record"):
        set_clause = ', '.join(
            [f"{column}='{value}'" for column, value in user_input.items() if column != id_column_name])
        update_query = f"UPDATE {table} SET {set_clause} WHERE {id_column_name}='{user_input[id_column_name]}';"
        execute_query(connection, update_query)
        st.success(f"Record Updated successfully in {table}!")


def delete_record(connection, db_name, table):
    if table == 'Borrowers':
        id_column_name = 'BorrowerID'
    elif table == 'Properties':
        id_column_name = 'PropertyID'
    elif table == 'MortgageLoans':
        id_column_name = 'LoanID'
    elif table == 'Payments':
        id_column_name = 'PaymentID'
    elif table == 'Guarantor_Cosigners':
        id_column_name = 'GuarantorID'
    elif table == 'Insurance':
        id_column_name = 'LoanID'
    else:
        st.error('Unknown table selected')  # Fallback
        id_column_name = 'ID'

    st.write(f'Enter the {id_column_name} of the record you want to delete')
    user_input = st.text_input(f"Enter {id_column_name}")
    if st.button("Delete Record"):
        delete_query = f"DELETE FROM {table} WHERE {id_column_name}='{user_input}';"
        execute_query(connection, delete_query)
        st.success(f"Record Deleted successfully from {table}!")



def main():
    # Database connection details should be in ENVs or a config file
    st.title("Mortgage Management System")
    host_name = os.getenv("MYSQL_HOST", "db")
    port = int(os.getenv("MYSQL_PORT", "3306"))
    user_name = os.getenv("MYSQL_USER")
    user_password = os.getenv("MYSQL_PASSWORD")
    db_name = os.getenv("MYSQL_DATABASE")

    db_connection = create_db_connection(host_name, port, user_name, user_password, db_name)

    menu = st.sidebar.selectbox(
        "Choose option:",
        ("Home", "Create record", "Read record", "Update record", "Delete record"),
    )
    table_selected = st.sidebar.selectbox(
        "Choose a table",
        ('Borrowers', 'Properties', 'MortgageLoans', 'Payments', 'Guarantor_Cosigners', 'Insurance')
    )

    if menu == "Home":
        st.header("Welcome to Mortgage Management System")

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
    main()