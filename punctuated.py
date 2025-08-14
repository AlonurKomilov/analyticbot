# punctuated.py — local stub to satisfy imports in bot/container.py
class Singleton:
    """
    Minimal callable singleton provider.
    Usage:
        my_dep = Singleton(MyClass, arg1, kw=value)
        inst = my_dep()  # returns single instance
    """
    def __init__(self, cls, *args, **kwargs):
        self._cls = cls
        self._args = args
        self._kwargs = kwargs
        self._instance = None

    def __call__(self):
        if self._instance is None:
            self._instance = self._cls(*self._args, **self._kwargs)
        return self._instance
