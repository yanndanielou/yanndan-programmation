# -*-coding:Utf-8 -*
""" Module that provides singleton , Cf 
https://stackoverflow.com/questions/6760685/what-is-the-best-way-of-implementing-singleton-in-python 
"""

class Singleton(type):
    """ Sigleton meta class """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
