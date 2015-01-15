ifdef VIRTUAL_ENV
	CFLAGS+= -I$(VIRTUAL_ENV)/include/python2.7/
else
	CFLAGS+= -I/use/include/python2.7/
endif

# NOTE: 
# -fno-strict-aliasing is required for cython
CFLAGS+= -Wall -fPIC -shared -O3 -fno-strict-aliasing
CXXFLAGS+= -std=c++0x

%.cpp: %.pyx
	cython --cplus --line-directives $<

%.so: %.cpp
	$(CXX) $(CXXFLAGS) $(CFLAGS) -o $@ $<

%.so: %.c
	$(CC) $(CFLAGS) -o $@ $<

