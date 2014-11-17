TOBUILD=linux

ifeq ($(TOBUILD),linux)
	SWIGARGS= --inplace
	PYEXE=python
else ifeq ($(TOBUILD),windows)
	SWIGARGS= -c mingw32
	PYEXE=C:\Python27\python.exe
endif

all:
	swig -Wall -c++ -python las13reader.i
ifeq ($(TOBUILD),windows)
	sed -i '14i\#include<cmath>\' las13reader_wrap.cxx
endif
	${PYEXE} setup.py build_ext ${SWIGARGS}

clean:
	rm -rf las13reader_wrap.cxx build/

cleanall:
	rm -rf las13reader.py _las13reader.so las13reader_wrap.cxx build/
