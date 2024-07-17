#include <iostream>
#include <string>
#include <sql.h>
#include <sqlext.h>

void write_to_sql_server(const std::string& data) {
    SQLHANDLE sqlEnvHandle;
    SQLHANDLE sqlConnHandle;
    SQLHANDLE sqlStmtHandle;
    SQLRETURN retCode;

    // Allocate environment handle
    if (SQL_SUCCESS != SQLAllocHandle(SQL_HANDLE_ENV, SQL_NULL_HANDLE, &sqlEnvHandle))
        return;

    // Set the ODBC version environment attribute
    if (SQL_SUCCESS != SQLSetEnvAttr(sqlEnvHandle, SQL_ATTR_ODBC_VERSION, (SQLPOINTER)SQL_OV_ODBC3, 0))
        return;

    // Allocate connection handle
    if (SQL_SUCCESS != SQLAllocHandle(SQL_HANDLE_DBC, sqlEnvHandle, &sqlConnHandle))
        return;

    // Connect to the database
    if (SQL_SUCCESS != SQLDriverConnect(sqlConnHandle, NULL,
        (SQLCHAR*)"DRIVER={SQL Server};SERVER=your_server;DATABASE=your_database;UID=your_username;PWD=your_password;",
        SQL_NTS, NULL, 0, NULL, SQL_DRIVER_NOPROMPT)) {
        SQLFreeHandle(SQL_HANDLE_DBC, sqlConnHandle);
        SQLFreeHandle(SQL_HANDLE_ENV, sqlEnvHandle);
        return;
    }

    // Allocate statement handle
    if (SQL_SUCCESS != SQLAllocHandle(SQL_HANDLE_STMT, sqlConnHandle, &sqlStmtHandle))
        return;

    // Write data to SQL Server (replace with your actual SQL query)
    std::string sqlQuery = "INSERT INTO your_table (column1) VALUES ('" + data + "');";
    if (SQL_SUCCESS != SQLExecDirect(sqlStmtHandle, (SQLCHAR*)sqlQuery.c_str(), SQL_NTS)) {
        SQLFreeHandle(SQL_HANDLE_STMT, sqlStmtHandle);
        SQLFreeHandle(SQL_HANDLE_DBC, sqlConnHandle);
        SQLFreeHandle(SQL_HANDLE_ENV, sqlEnvHandle);
        return;
    }

    // Free handles
    SQLFreeHandle(SQL_HANDLE_STMT, sqlStmtHandle);
    SQLFreeHandle(SQL_HANDLE_DBC, sqlConnHandle);
    SQLFreeHandle(SQL_HANDLE_ENV, sqlEnvHandle);
}

int main() {
    write_to_sql_server("Sample data");
    return 0;
}
