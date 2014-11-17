
#!/usr/bin/env python

"""
setup.py file for las13reader 
"""

from distutils.core import setup, Extension
import os

#if windows then statically link the libstdc++ and libgcc - this assumes using mingw32 to compile
if os.name=='nt':
   las13reader_module = Extension('_las13reader',
                           sources=['las13reader_wrap.cxx', '../las13reader/src/Las1_3_handler.cpp',
                                 '../las13reader/src/Pulse.cpp','../las13reader/src/PulseManager.cpp','../las13reader/src/vec3d.cpp'],
                           extra_compile_args=["-std=c++0x"],
                           extra_link_args=["-lstdc++","-lgcc"]
                           )

else:
   las13reader_module = Extension('_las13reader',
                           sources=['las13reader_wrap.cxx', '../las13reader/src/Las1_3_handler.cpp',
                                 '../las13reader/src/Pulse.cpp','../las13reader/src/PulseManager.cpp','../las13reader/src/vec3d.cpp'],
                           extra_compile_args=["-std=c++0x"]
                           )

setup (name = 'las13reader',
       version = '0.1',
       author      = "mmi+arsf",
       description = """las13reader swig""",
       ext_modules = [las13reader_module],
       py_modules = ["las13reader"],
       )

