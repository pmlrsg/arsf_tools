#basic makefile

CC=g++
CFLAGS=-pipe -std=gnu++0x -std=c++0x -O4 -Wall -m64 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -fpic
LDFLAGS= -lm -shared
SOURCES=src/Las1_3_handler.cpp src/Pulse.cpp src/PulseManager.cpp src/vec3d.cpp
OBJECTS=$(SOURCES:.cpp=.o)
LIBNAME=liblas13reader.so
TESTEXE=tester

all:$(SOURCES) $(LIBNAME)

$(LIBNAME): $(OBJECTS)
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

.cpp.o:
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm $(OBJECTS)

cleanall:
	rm  $(LIBNAME) $(TESTEXE) $(OBJECTS)

#test executable to see if lib compiled ok
test:
	g++ $(CFLAGS) src/main.cpp liblas13reader.so -o $(TESTEXE) 

