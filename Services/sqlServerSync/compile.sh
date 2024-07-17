g++ -I"$JAVA_HOME/include" -I"$JAVA_HOME/include/darwin" -shared -o InfluxDBClient.so -fPIC InfluxDBClient.cpp -lcurl
