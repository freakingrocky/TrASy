#include <iostream>
#include <sstream>
#include <cstdlib>
#include <sql.h>
#include <sqlext.h>
#include <sqltypes.h>
#include <json/json.h>  // Include the jsoncpp header file

using namespace std;

const char* dsn = "INFLUX_HISTORICAL_SYMBOLS";
const char* user = "sqlAccesser";
const char* password = "sqlPasswordSimple";
const char* host = "192.168.64.1\\SQLEXPRESS";

bool extractQuery(const string& input, string* query) {
    try {
        // Parse the incoming JSON body
        Json::Value root;
        Json::CharReaderBuilder reader;
        string errors;
        istringstream bodyStream(input);
        if (!Json::parseFromStream(reader, bodyStream, &root, &errors)) {
            *query = "Invalid JSON: " + errors;
            return false;
        }

        *query = root["query"].asString();
        return true;
    } catch (exception& e) {
        *query = "Error parsing JSON: " + string(e.what());
        return false;
    }
}

string executeSQLQuery(const string& input) {
    string query;
    if (!extractQuery(input, &query)) {
        // Handle the error case
        return query;
    }
    cout << "Executing SQL Query: " << query << endl;
    SQLHENV hEnv = NULL;
    SQLHDBC hDbc = NULL;
    SQLHSTMT hStmt = NULL;
    SQLRETURN retcode;
    ostringstream result;
    Json::Value jsonData(Json::arrayValue);

    if (query.find("Error") != string::npos) {
        return query;
    }


    if (!dsn || !user || !password || !host) {
        result << "Environment variables for DB credentials not set.";
        return result.str();
    }

    // Construct the connection string using the environment variables
    string connectionString = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=" + string(host) + ";DATABASE=" + string(dsn) + ";UID=" + string(user) + ";PWD=" + string(password) + ";TrustServerCertificate=yes;";

    // Allocate environment handle
    retcode = SQLAllocHandle(SQL_HANDLE_ENV, SQL_NULL_HANDLE, &hEnv);
    if (retcode != SQL_SUCCESS && retcode != SQL_SUCCESS_WITH_INFO) {
        result << "Error allocating environment handle.";
        return result.str();
    }

    // Set the ODBC version environment attribute
    retcode = SQLSetEnvAttr(hEnv, SQL_ATTR_ODBC_VERSION, (void*)SQL_OV_ODBC3, 0);
    if (retcode != SQL_SUCCESS && retcode != SQL_SUCCESS_WITH_INFO) {
        result << "Error setting ODBC version.";
        SQLFreeHandle(SQL_HANDLE_ENV, hEnv);
        return result.str();
    }

    // Allocate connection handle
    retcode = SQLAllocHandle(SQL_HANDLE_DBC, hEnv, &hDbc);
    if (retcode != SQL_SUCCESS && retcode != SQL_SUCCESS_WITH_INFO) {
        result << "Error allocating connection handle.";
        SQLFreeHandle(SQL_HANDLE_ENV, hEnv);
        return result.str();
    }

    // Set login timeout to 5 seconds
    SQLSetConnectAttr(hDbc, SQL_LOGIN_TIMEOUT, (SQLPOINTER)5, 0);

    // Connect to data source
    retcode = SQLDriverConnect(hDbc, NULL, (SQLCHAR*)connectionString.c_str(), SQL_NTS, NULL, 0, NULL, SQL_DRIVER_COMPLETE);
    if (retcode != SQL_SUCCESS && retcode != SQL_SUCCESS_WITH_INFO) {
        SQLCHAR SqlState[1024];
        SQLCHAR Msg[1024];
        SQLINTEGER NativeError;
        SQLSMALLINT MsgLen;
        SQLGetDiagRec(SQL_HANDLE_DBC, hDbc, 1, SqlState, &NativeError, Msg, sizeof(Msg), &MsgLen);
        result << "Error connecting to data source. State: " << SqlState << " Message: " << Msg;
        SQLFreeHandle(SQL_HANDLE_DBC, hDbc);
        SQLFreeHandle(SQL_HANDLE_ENV, hEnv);
        return result.str();
    }

    // Allocate statement handle
    retcode = SQLAllocHandle(SQL_HANDLE_STMT, hDbc, &hStmt);
    if (retcode != SQL_SUCCESS && retcode != SQL_SUCCESS_WITH_INFO) {
        result << "Error allocating statement handle.";
        SQLDisconnect(hDbc);
        SQLFreeHandle(SQL_HANDLE_DBC, hDbc);
        SQLFreeHandle(SQL_HANDLE_ENV, hEnv);
        return result.str();
    }

    // Execute SQL statement
    retcode = SQLExecDirect(hStmt, (SQLCHAR*)query.c_str(), SQL_NTS);
    if (retcode != SQL_SUCCESS && retcode != SQL_SUCCESS_WITH_INFO) {
        SQLCHAR SqlState[1024];
        SQLCHAR Msg[1024];
        SQLINTEGER NativeError;
        SQLSMALLINT MsgLen;
        SQLGetDiagRec(SQL_HANDLE_STMT, hStmt, 1, SqlState, &NativeError, Msg, sizeof(Msg), &MsgLen);
        result << "Error executing SQL query. State: " << SqlState << " Message: " << Msg;
        SQLFreeHandle(SQL_HANDLE_STMT, hStmt);
        SQLDisconnect(hDbc);
        SQLFreeHandle(SQL_HANDLE_DBC, hDbc);
        SQLFreeHandle(SQL_HANDLE_ENV, hEnv);
        return result.str();
    }

    // Get column count
    SQLSMALLINT columns;
    SQLNumResultCols(hStmt, &columns);

    // Process data
    SQLCHAR buffer[256];
    SQLLEN indicator;
    while (SQLFetch(hStmt) == SQL_SUCCESS) {
        Json::Value row(Json::objectValue);
        for (SQLUSMALLINT i = 1; i <= columns; i++) {
            SQLCHAR columnName[256];
            SQLSMALLINT nameLength;
            SQLDescribeCol(hStmt, i, columnName, sizeof(columnName), &nameLength, NULL, NULL, NULL, NULL);
            SQLGetData(hStmt, i, SQL_C_CHAR, buffer, sizeof(buffer), &indicator);
            row[(char*)columnName] = (indicator == SQL_NULL_DATA) ? Json::Value::null : Json::Value((char*)buffer);
        }
        jsonData.append(row);
    }

    // Cleanup
    SQLFreeHandle(SQL_HANDLE_STMT, hStmt);
    SQLDisconnect(hDbc);
    SQLFreeHandle(SQL_HANDLE_DBC, hDbc);
    SQLFreeHandle(SQL_HANDLE_ENV, hEnv);

    Json::StreamWriterBuilder writer;
    string jsonString = Json::writeString(writer, jsonData);
    return jsonString;
}
