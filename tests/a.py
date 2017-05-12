#-*- coding: UTF-8 -*-
import time

def foo():
    print('do something~')
def timeit(func):
    start=0
    def wrapper():
        start=time.clock()
    func()
    end=time.clock()
    print('used :',end-start)
    return wrapper
foo=timeit(foo)
foo()