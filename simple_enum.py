import inspect


class SimpleEnum:
    @classmethod
    def to_dict(cls):
        if not hasattr(cls, '__ENUM_DICT__'):
            setattr(cls, '__ENUM_DICT__', {k: v for k, v 
                in inspect.getmembers(cls, lambda a: not inspect.isroutine(a))
                if not k.startswith('__')})

        return cls.__ENUM_DICT__

