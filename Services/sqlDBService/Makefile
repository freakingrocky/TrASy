CXX = g++
CXXFLAGS = -std=c++11 -O2 -Wall -I/usr/include/jsoncpp -I/usr/include -I/usr/local/include
LDFLAGS = -L/usr/lib -L/usr/local/lib -lboost_system -lpthread -lodbc -ljsoncpp

TARGET = sqlDBService
SRCS = main.cpp sql.cpp
HEADERS = sql.h

all: $(TARGET)

$(TARGET): $(SRCS) $(HEADERS)
	$(CXX) $(CXXFLAGS) $(SRCS) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)
