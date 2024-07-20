CXX = g++
CXXFLAGS = -std=c++11 -O2 -Wall -I/usr/include/jsoncpp -I/usr/local/include -I/usr/include
LIBS = -L/usr/lib -L/usr/local/lib -lboost_system -lboost_thread -lssl -lcrypto -lpthread -ljsoncpp

TARGET = testService
SRCS = main.cpp functions.cpp influxdb.cpp

all: $(TARGET)

$(TARGET): $(SRCS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRCS) $(LIBS)

clean:
	rm -f $(TARGET)
