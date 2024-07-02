g++ -I"%JAVA_HOME%/include" -I"%JAVA_HOME%/include/win32" -shared -o InfluxDBClient.dll -fPIC InfluxDBClient.cpp -lcurl
