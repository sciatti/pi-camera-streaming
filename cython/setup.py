from setuptools import setup
from Cython.Build import cythonize

setup(
    name='Motion Detection Speed Test',
    ext_modules=cythonize("motionSpeed.pyx"),
    zip_safe=False,
)