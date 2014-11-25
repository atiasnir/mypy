
ifdef VIRTUAL_ENV
	CFLAGS+= -I$(VIRTUAL_ENV)/include/python2.7/
else
	CFLAGS+= -I/use/include/python2.7/
endif

CFLAGS+= -std=c++0x -Wall -fPIC -shared -O3 
CFLAGS+= -fno-strict-aliasing # required for cython

%.cpp: %.pyx
	cython --cplus $<

%.so: %.cpp
	$(CXX) $(CFLAGS) -o $@ $<
