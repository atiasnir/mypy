CFLAGS+= -I/home/bnet/atiasnir/mypy/include/python2.7/
CFLAGS+= -std=c++0x -Wall -fPIC -shared -O3 -fno-strict-aliasing
#CXX=g++-4.8

%.cpp: %.pyx
	cython --cplus $<

%.so: %.cpp
	$(CXX) $(CFLAGS) -o $@ $<
