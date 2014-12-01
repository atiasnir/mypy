ifdef VIRTUAL_ENV
	CFLAGS+= -I$(VIRTUAL_ENV)/include/python2.7/
else
	CFLAGS+= -I/use/include/python2.7/
endif

# NOTE: 
# -fno-strict-aliasing is required for cython
CFLAGS+= -std=c++0x -Wall -fPIC -shared -O3 -fno-strict-aliasing

%.cpp: %.pyx
	cython --cplus $<

%.so: %.cpp
	$(CXX) $(CFLAGS) -o $@ $<
