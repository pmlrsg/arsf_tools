all:
	swig -Wall -c++ -python  las13reader.i
	python setup.py build_ext --inplace

clean:
	rm -rf las13reader_wrap.cxx build/

cleanall:
	rm -rf las13reader.py _las13reader.so las13reader_wrap.cxx build/
