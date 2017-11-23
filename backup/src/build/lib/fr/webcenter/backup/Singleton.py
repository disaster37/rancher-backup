__author__ = 'disaster'

class Singleton(type):
    def __init__(cls,name,bases,dic):
        super(Singleton,cls).__init__(name,bases,dic)
        cls.instance=None
    def __call__(cls,*args,**kw):
        if cls.instance is None:
            cls.instance=super(Singleton,cls).__call__(*args,**kw)
        return cls.instance

    def _drop(cls):
        cls.instance=None

