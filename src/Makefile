BOOST_HOME?=/home/bnet/atiasnir/cpp/boost_1_53_0

ifeq ($(COMPILE_TYPE),Debug)
CFLAGS+= -msse2 -g
else
CFLAGS+= -O3 -msse2 -g
endif
CFLAGS+=  -isystem /home/bnet/atiasnir/app/include -isystem /home/bnet/atiasnir/app/include/python2.7

# BOOST
CFLAGS+= -I${BOOST_HOME} -Wno-deprecated
LDFLAGS+= -L${BOOST_HOME}/stage/lib  -L/home/bnet/atiasnir/mypy/lib -lboost_python -lboost_system -lboost_numpy

# General
CFLAGS+= -m64 -fPIC -fexceptions -std=c++0x -Wno-strict-aliasing -I./numpy -L./numpy
LDFLAGS+= -lm -pthread -L/home/bnet/atiasnir/app/lib
#-shared
LDFLAGS+= -lpython2.7 
CXX=g++-4.7.2

.PHONY: clean all
all: netrand.so

netrand.so: netrand.o
	$(CXX) $(CFLAGS) -o $@ $^ $(LDFLAGS) -shared

clean:
	$(RM) -f *.o *.so *~ *.d brute_test test test_color

%.o: %.cpp
	$(CXX) -c $(CFLAGS) -Wall -o $@ $<

%.o: %.h
