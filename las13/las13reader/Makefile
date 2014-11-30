#basic makefile
#Note the windows build may not work :)

TOBUILD=linux

#for linux build
ifeq ($(TOBUILD),linux)
	CC=g++
	CFLAGS=-pipe -std=gnu++0x -std=c++0x -O4 -Wall -m64 -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -fpic
	LDLIBFLAGS= -shared
	LDEXEFLAGS=
	LIBNAME=liblas13reader.so
	TESTEXE=tester

#for windows build (from a linux machine)
else ifeq ($(TOBUILD),windows)
	CC=i686-w64-mingw32-g++
	CFLAGS=-pipe -std=gnu++0x -std=c++0x -O4 -Wall -D_LARGEFILE64_SOURCE -D_LARGEFILE_SOURCE -fpic
	LDLIBFLAGS= -shared -lstdc++ -lgcc
	LDEXEFLAGS= -lstdc++ -lgcc
	LIBNAME=liblas13reader.dll
	TESTEXE=tester.exe
endif

SOURCES=src/Las1_3_handler.cpp src/Pulse.cpp src/PulseManager.cpp src/vec3d.cpp
OBJECTS=$(SOURCES:.cpp=.o)


all:$(SOURCES) $(LIBNAME) test

$(LIBNAME): $(OBJECTS)
	$(CC) $(LDLIBFLAGS) $(OBJECTS) -o $@

.cpp.o:
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf $(OBJECTS)

cleanall:
	rm  -rf $(LIBNAME) $(TESTEXE) $(OBJECTS)

#test executable to see if lib compiled ok
test:
	$(CC) $(CFLAGS) $(LDEXEFLAGS) src/main.cpp $(LIBNAME) -o $(TESTEXE) 

