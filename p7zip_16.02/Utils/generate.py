#!/usr/bin/env python

import os
import sys

class Structure:
	def __init__(self, **kwds):
		self.__dict__.update(kwds)

TYPE_EXE=0
TYPE_DLL=1

def generate_pro(filename,project):
	
	if os.path.isfile(filename):
		os.remove(filename)

	f=open(filename,'w')
	f.write('''
# WARNING : automatically generated by utils/generate.py

QT -= core gui
TARGET = ''' + project.name   + '''
''')
	if project.type == TYPE_EXE:
		f.write('''
CONFIG += console
CONFIG -= app_bundle
TEMPLATE = app
''')
	if project.type == TYPE_DLL:
		f.write('''
CONFIG += dll
TEMPLATE = lib
''')

	f.write('''
DESTDIR = ../../../../bin

unix: LIBS += -ldl

DEFINES+=USE_LIB7Z_DLL

''')
	f.write('INCLUDEPATH = \\\n')
	for file in project.includedirs:
		f.write("  {} \\\n".format(file))
	f.write('\n')
	for d in project.defines:
		f.write("DEFINES += " + d + '\n')	
	f.write('\n')
	f.write('SOURCES +=  \\\n')
	for file in project.files_c:
		f.write("  ../../../../{} \\\n".format(file))
	for file in project.files_cpp:
		f.write("  ../../../../{} \\\n".format(file))

	f.write('''
macx: LIBS += -framework CoreFoundation
''')
	f.write('\n')
	f.close()

premake4_headers='''
-- WARNING : automatically generated by utils/generate.py
solution "p7zip"
   configurations { "Debug", "Release" }

-- includes for all projects
      includedirs {
'''

def generate_premake4(filename,project):
	
	if os.path.isfile(filename):
		os.remove(filename)

	f=open(filename,'w')
	f.write(premake4_headers)
	for file in project.includedirs:
		f.write('        "{}",\n'.format(file))
	f.write('      }\n\n')
	defines=""
	for d in project.defines:
		defines+= ', "' + d + '"'	
	f.write('      configuration "Debug"\n')
	f.write('         defines { "DEBUG"' + defines + ' }\n')
	f.write('         flags { "Symbols" }\n')
	f.write('\n')
	f.write('      configuration "Release"\n')
	f.write('         defines { "NDEBUG"' + defines + ' }\n')
	f.write('         flags { "Optimize" }    \n')
	f.write('\n')
	f.write('   project "all_c_code"\n')
	f.write('     kind "StaticLib"\n')
	f.write('      language "C"\n')
	f.write('      files {\n')
	for file in project.files_c:
		f.write('      "../../../../{}",\n'.format(file))
	f.write('''      }
 
---------------------------------
   project "''' + project.name + '''"
      kind "ConsoleApp"
      language "C++"
      files {
''')
	for file in project.files_cpp:
		f.write('      "../../../../{}",\n'.format(file))
	f.write('''
      }

      configuration "linux"
	links       {  "all_c_code", "pthread" } 
''')

	f.close()

def generate_cmake(filename,project):
	
	if os.path.isfile(filename):
		os.remove(filename)

	f=open(filename,'w')
	f.write('''

# WARNING : automatically generated by utils/generate.py
cmake_minimum_required(VERSION 2.8)

''')
	f.write('include_directories(\n')
	for file in project.includedirs:
		f.write('  "{}"\n'.format(file))
	f.write(')\n\n')
	defines=""
	for d in project.defines:
		defines+= ' -D' + d
	f.write('add_definitions(' + defines + ')\n')
	f.write('''
IF(APPLE)
  add_definitions(-DENV_MACOSX)
  FIND_LIBRARY(COREFOUNDATION_LIBRARY CoreFoundation )
ENDIF(APPLE)

''')
	if project.type == TYPE_EXE:
		f.write('add_executable(' + project.name2 + '\n\n')
	if project.type == TYPE_DLL:
		f.write('add_library(' + project.name2 + ' MODULE\n\n')
	for file in project.files_c:
		f.write('  "../../../../{}"\n'.format(file))
	for file in project.files_cpp:
		f.write('  "../../../../{}"\n'.format(file))
	f.write(')\n')
	f.write(project.cmake_end)
	f.close()

def to_obj(file):
	file2=os.path.basename(file)
	return os.path.splitext(file2)[0] + '.o'

def generate_makefile_list(filename,project,bin_dir='../../../../bin'):
	
	if os.path.isfile(filename):
		os.remove(filename)

	f=open(filename,'w')
	f.write('''

# WARNING : automatically generated by utils/generate.py

''')
	if project.type == TYPE_EXE:
		f.write('PROG={}/{}$(BINSUFFIX)\n\n'.format(bin_dir,project.name))
	if project.type == TYPE_DLL:
		f.write('PROG={}/{}.so\n\n'.format(bin_dir,project.name))

	f.write('all: $(PCH_NAME) $(PROG)\n\n')

	f.write('LOCAL_FLAGS=$(TARGET_FLAGS) \\\n')
	for d in project.defines:
		f.write('  -D{} \\\n'.format(d))	
	f.write('\n')
	f.write('SRCS=\\\n')
	for file in project.files_cpp:
		f.write('  ../../../../{} \\\n'.format(file))
	f.write('\n')
	f.write('SRCS_C=\\\n')
	for file in project.files_c:
		f.write('  ../../../../{} \\\n'.format(file))
	f.write('''
StdAfx.h.gch : ../../../myWindows/StdAfx.h
\trm -f StdAfx.h.gch
\t$(CXX) $(CXXFLAGS) ../../../myWindows/StdAfx.h -o StdAfx.h.gch
''')

	for file in project.files_c:
		file='../../../../' + file
		f.write('{} : {}\n'.format(to_obj(file),file))
		f.write('\t$(CC) $(CFLAGS) {}\n'.format(file))
	for file in project.files_cpp:
		file='../../../../' + file
		f.write('{} : {}\n'.format(to_obj(file),file))
		f.write('\t$(CXX) $(CXXFLAGS) {}\n'.format(file))

	f.write('\nOBJS=\\\n')
	for file in project.files_c:
		file=to_obj(file)
		if file == '7zCrcOpt.o':
			f.write(' $(OBJ_CRC32) \\\n')
		else:
			f.write(' {} \\\n'.format(file))
	for file in project.files_cpp:
		f.write(' {} \\\n'.format(to_obj(file)))
	if project.need_AES:
		f.write(' $(OBJ_AES) \\\n')
		
	f.write('\n')


	f.close()

def generate_android_mk(filename,project):

	if os.path.isfile(filename):
		os.remove(filename)

	f=open(filename,'w')
	f.write('''# 
# build {} for armeabi and armeabi-v7a CPU
#
# WARNING : file generated by generate.py
#


LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE := {}
'''.format(project.name,project.name))
	f.write(project.android_header)
	f.write('LOCAL_SRC_FILES := \\\n')
	for file in project.files_cpp:
		f.write('  ../../../../{} \\\n'.format(file))
	for file in project.files_c:
		f.write('  ../../../../{} \\\n'.format(file))

	f.write('\n')
	if project.type == TYPE_EXE:
		f.write('# Needed since ANDROID 5, these programs run on android-16 (Android 4.1+)\n')
		f.write('LOCAL_CFLAGS += -fPIE\n')
		f.write('LOCAL_LDFLAGS += -fPIE -pie\n')
		f.write('\n')
		f.write('include $(BUILD_EXECUTABLE)\n\n')
	if project.type == TYPE_DLL:
		# nothing to do here
		f.write('include $(BUILD_SHARED_LIBRARY)\n\n')
	f.close()

includedirs_7za=[
 "../../../myWindows",
 "../../../",
 "../../../include_windows"
]


includedirs_lzham=[  # FIXME
 "../../../../CPP/7zip/Compress/Lzham/include",
 "../../../../CPP/7zip/Compress/Lzham/lzhamcomp",
 "../../../../CPP/7zip/Compress/Lzham/lzhamdecomp",
 "../../../myWindows",
 "../../../",
 "../../../../",
 "../../../include_windows"
]

includedirs_zstd=[  # FIXME
 "../../../../C",
 "../../../../C/ZStd",
 "../../../../CPP/7zip/Compress",
 "../../../myWindows",
 "../../../",
 "../../../../",
 "../../../include_windows"
]

import file_7za
import file_7zCon_sfx
import file_7z
import file_7zr
import file_7zG
import file_7zFM
import file_7z_so
import file_Codecs_Rar_so
import file_Codecs_Lzham_so
import file_Codecs_ZStd_so
import file_LzmaCon
import file_Client7z
import file_P7ZIP
import file_TestUI


project_7za=Structure(name="7za",name2="7za",
	type=TYPE_EXE,
	need_AES=True,
	includedirs=includedirs_7za,
	defines=[ "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_7za.files_c,
	files_cpp=file_7za.files_cpp,
	cmake_end='''

IF(APPLE)
   TARGET_LINK_LIBRARIES(7za ${COREFOUNDATION_LIBRARY} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(7za ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''',
android_header=r'''
LOCAL_CFLAGS := -DANDROID_NDK  -fexceptions \
	-DNDEBUG -D_REENTRANT -DENV_UNIX \
	-DBREAK_HANDLER \
	-DUNICODE -D_UNICODE -DUNIX_USE_WIN_FILE \
	-I../../../7zip/Archive \
	-I../../../7zip/Archive/7z \
	-I../../../7zip/Archive/BZip2 \
	-I../../../7zip/Archive/Common \
	-I../../../7zip/Archive/GZip \
	-I../../../7zip/Archive/Cab \
	-I../../../7zip/Archive/Lzma \
	-I../../../7zip/Archive/Tar \
	-I../../../7zip/Archive/Zip \
	-I../../../7zip/Archive/Split \
	-I../../../7zip/Archive/Z \
	-I../../../7zip/Compress \
       	-I../../../7zip/Crypto \
	-I../../../7zip/UI/Console \
	-I../../../7zip/UI/Common \
	-I../../../Windows \
	-I../../../Common \
	-I../../../7zip/Common \
	-I../../../../C \
-I../../../myWindows \
-I../../../ \
-I../../../include_windows

''')

project_7zr=Structure(name="7zr",name2="7zr",
	type=TYPE_EXE,
	need_AES=True,
	includedirs=includedirs_7za,
	defines=[ "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "_NO_CRYPTO", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_7zr.files_c,
	files_cpp=file_7zr.files_cpp,
	cmake_end='''

IF(APPLE)
   TARGET_LINK_LIBRARIES(7zr ${COREFOUNDATION_LIBRARY} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(7zr ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''',
android_header=r'''
LOCAL_CFLAGS := -DANDROID_NDK  -fexceptions \
	-DNDEBUG -D_REENTRANT -DENV_UNIX \
	-DBREAK_HANDLER -D_NO_CRYPTO \
	-DUNICODE -D_UNICODE -DUNIX_USE_WIN_FILE \
	-I../../../7zip/Archive \
	-I../../../7zip/Archive/7z \
	-I../../../7zip/Archive/BZip2 \
	-I../../../7zip/Archive/Common \
	-I../../../7zip/Archive/GZip \
	-I../../../7zip/Archive/Cab \
	-I../../../7zip/Archive/Lzma \
	-I../../../7zip/Archive/Tar \
	-I../../../7zip/Archive/Zip \
	-I../../../7zip/Archive/Split \
	-I../../../7zip/Archive/Z \
	-I../../../7zip/Compress \
       	-I../../../7zip/Crypto \
	-I../../../7zip/UI/Console \
	-I../../../7zip/UI/Common \
	-I../../../Windows \
	-I../../../Common \
	-I../../../7zip/Common \
	-I../../../../C \
-I../../../myWindows \
-I../../../ \
-I../../../include_windows

''')

project_7zCon_sfx=Structure(name="7zCon.sfx",name2="7zCon.sfx",
	type=TYPE_EXE,
	need_AES=True,
	includedirs=includedirs_7za,
	defines=[ "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE", "EXTRACT_ONLY", "NO_READ_FROM_CODER", "_SFX" ],
	files_c=file_7zCon_sfx.files_c,
	files_cpp=file_7zCon_sfx.files_cpp,
	cmake_end='''

IF(APPLE)
   TARGET_LINK_LIBRARIES(7zCon.sfx ${COREFOUNDATION_LIBRARY} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(7zCon.sfx ${CMAKE_THREAD_LIBS_INIT})
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''')

project_7z=Structure(name="7z",name2="7z_",
	type=TYPE_EXE,
	need_AES=False,
	includedirs=includedirs_7za,
	defines=[ "EXTERNAL_CODECS", "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_7z.files_c,
	files_cpp=file_7z.files_cpp,
	cmake_end='''

find_library(DL_LIB dl)

link_directories(${DL_LIB_PATH})

IF(APPLE)
   TARGET_LINK_LIBRARIES(7z_ ${COREFOUNDATION_LIBRARY} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(7z_ ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''',
android_header=r'''
LOCAL_CFLAGS := -DANDROID_NDK  -fexceptions \
	-DNDEBUG -D_REENTRANT -DENV_UNIX \
	-DEXTERNAL_CODECS \
	-DBREAK_HANDLER \
	-DUNICODE -D_UNICODE -DUNIX_USE_WIN_FILE \
	-I../../../Windows \
	-I../../../Common \
	-I../../../../C \
-I../../../myWindows \
-I../../../ \
-I../../../include_windows
''')

project_Codecs_Rar=Structure(name="Rar",name2="Rar",
	type=TYPE_DLL,
	need_AES=False,
	includedirs=includedirs_7za,
	defines=[ "EXTERNAL_CODECS", "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_Codecs_Rar_so.files_c,
	files_cpp=file_Codecs_Rar_so.files_cpp,
	cmake_end='''

find_library(DL_LIB dl)

link_directories(${DL_LIB_PATH})

IF(APPLE)
   TARGET_LINK_LIBRARIES(Rar ${COREFOUNDATION_LIBRARY} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(Rar ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''',
android_header=r'''
LOCAL_CFLAGS := -DANDROID_NDK  -fexceptions \
	-DNDEBUG -D_REENTRANT -DENV_UNIX \
	-DEXTERNAL_CODECS \
	-DBREAK_HANDLER \
	-DUNICODE -D_UNICODE -DUNIX_USE_WIN_FILE \
	-I../../../Windows \
	-I../../../Common \
	-I../../../../C \
-I../../../myWindows \
-I../../../ \
-I../../../include_windows
''')


project_Codecs_ZStd=Structure(name="ZStd",name2="ZStd",
	type=TYPE_DLL,
	need_AES=False,
	includedirs=includedirs_zstd,
	defines=[ "EXTERNAL_CODECS", "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_Codecs_ZStd_so.files_c,
	files_cpp=file_Codecs_ZStd_so.files_cpp,
	cmake_end='''
find_library(DL_LIB dl)

link_directories(${DL_LIB_PATH})

IF(APPLE)
   TARGET_LINK_LIBRARIES(ZStd ${COREFOUNDATION_LIBRARY} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(ZStd ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)
''',
android_header=r'''
LOCAL_CFLAGS := -DANDROID_NDK  -fexceptions \
	-DNDEBUG -D_REENTRANT -DENV_UNIX \
	-DEXTERNAL_CODECS \
	-DBREAK_HANDLER \
	-DUNICODE -D_UNICODE -DUNIX_USE_WIN_FILE \
	-I../../../Windows \
	-I../../../Common \
	-I../../../../C \
-I../../../myWindows \
-I../../../ \
-I../../../include_windows \
-I../../../../C/ZStd \
-I../../../../CPP/7zip/Compress \
-I../../../../CPP/7zip/Common

''')

project_Codecs_Lzham=Structure(name="Lzham",name2="Lzham",
	type=TYPE_DLL,
	need_AES=False,
	includedirs=includedirs_lzham,
	defines=[ "EXTERNAL_CODECS", "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_Codecs_Lzham_so.files_c,
	files_cpp=file_Codecs_Lzham_so.files_cpp,
	cmake_end='''

find_library(DL_LIB dl)

link_directories(${DL_LIB_PATH})

IF(APPLE)
   TARGET_LINK_LIBRARIES(Lzham ${COREFOUNDATION_LIBRARY} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(Lzham ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''',
android_header=r'''
LOCAL_CFLAGS := -DANDROID_NDK  -fexceptions \
	-DNDEBUG -D_REENTRANT -DENV_UNIX \
	-DEXTERNAL_CODECS \
	-DBREAK_HANDLER \
	-DUNICODE -D_UNICODE -DUNIX_USE_WIN_FILE \
	-I../../../Windows \
	-I../../../Common \
	-I../../../../C \
-I../../../myWindows \
-I../../../ \
-I../../../include_windows \
-I../../../../CPP/7zip/Compress/Lzham/include \
-I../../../../CPP/7zip/Compress/Lzham/lzhamcomp \
-I../../../../CPP/7zip/Compress/Lzham/lzhamdecomp

''')


project_7zG=Structure(name="7zG",name2="7zG",
	type=TYPE_EXE,
	need_AES=False,
	includedirs=includedirs_7za,
	defines=[ "LANG",  "EXTERNAL_CODECS", "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_7zG.files_c,
	files_cpp=file_7zG.files_cpp,
	cmake_end='''

IF(APPLE)
  add_definitions(-DENV_MACOSX  -D__WXMAC__)
ENDIF(APPLE)

find_package(wxWidgets COMPONENTS core base adv REQUIRED)

find_library(DL_LIB dl)

include( ${wxWidgets_USE_FILE} )

link_directories(${DL_LIB_PATH})

IF(APPLE)
   TARGET_LINK_LIBRARIES(7zG ${COREFOUNDATION_LIBRARY} ${wxWidgets_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(7zG ${wxWidgets_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''')

project_7zFM=Structure(name="7zFM_do_not_use",name2="7zFM_do_not_use",
	type=TYPE_EXE,
	need_AES=False,
	includedirs=includedirs_7za,
	defines=[ "LANG", "NEW_FOLDER_INTERFACE", "EXTERNAL_CODECS", "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_7zFM.files_c,
	files_cpp=file_7zFM.files_cpp,
	cmake_end='''

IF(APPLE)
  add_definitions(-DENV_MACOSX  -D__WXMAC__)
ENDIF(APPLE)

find_package(wxWidgets COMPONENTS core base adv REQUIRED)

find_library(DL_LIB dl)

include( ${wxWidgets_USE_FILE} )

link_directories(${DL_LIB_PATH})

IF(APPLE)
   TARGET_LINK_LIBRARIES(7zFM_do_not_use ${COREFOUNDATION_LIBRARY} ${wxWidgets_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(7zFM_do_not_use ${wxWidgets_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''')

project_Format7zFree=Structure(name="7z",name2="7z",
	type=TYPE_DLL,
	need_AES=True,
	includedirs=includedirs_7za,
	defines=[ "EXTERNAL_CODECS", "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_7z_so.files_c,
	files_cpp=file_7z_so.files_cpp,
	cmake_end='''

SET_TARGET_PROPERTIES(7z PROPERTIES PREFIX "")

IF(APPLE)
   TARGET_LINK_LIBRARIES(7z ${COREFOUNDATION_LIBRARY} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(7z ${CMAKE_THREAD_LIBS_INIT})
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)
	
''',
android_header=r'''
LOCAL_CFLAGS := -DANDROID_NDK  -fexceptions \
	-DNDEBUG -D_REENTRANT -DENV_UNIX \
	-DEXTERNAL_CODECS \
	-DUNICODE -D_UNICODE -DUNIX_USE_WIN_FILE \
	-I../../../Windows \
	-I../../../Common \
	-I../../../../C \
	-I../../../myWindows \
	-I../../../ \
	-I../../../include_windows

''')

project_LzmaCon=Structure(name="LzmaCon",name2="LzmaCon",
	type=TYPE_EXE,
	need_AES=True,
	includedirs=includedirs_7za,
	defines=[ "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX"  ],
	files_c=file_LzmaCon.files_c,
	files_cpp=file_LzmaCon.files_cpp,
	cmake_end='''

IF(APPLE)
   TARGET_LINK_LIBRARIES(LzmaCon ${COREFOUNDATION_LIBRARY} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(LzmaCon ${CMAKE_THREAD_LIBS_INIT})
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''',
android_header=r'''
LOCAL_CFLAGS := -DANDROID_NDK  -fexceptions \
	-DNDEBUG -D_REENTRANT -DENV_UNIX \
	-I../../../7zip/Archive \
	-I../../../7zip/Archive/7z \
	-I../../../7zip/Archive/BZip2 \
	-I../../../7zip/Archive/Common \
	-I../../../7zip/Archive/GZip \
	-I../../../7zip/Archive/Cab \
	-I../../../7zip/Archive/Lzma \
	-I../../../7zip/Archive/Tar \
	-I../../../7zip/Archive/Zip \
	-I../../../7zip/Archive/Split \
	-I../../../7zip/Archive/Z \
	-I../../../7zip/Compress \
       	-I../../../7zip/Crypto \
	-I../../../7zip/UI/Console \
	-I../../../7zip/UI/Common \
	-I../../../Windows \
	-I../../../Common \
	-I../../../7zip/Common \
	-I../../../../C \
-I../../../myWindows \
-I../../../ \
-I../../../include_windows

''')

project_Client7z=Structure(name="Client7z",name2="Client7z",
	type=TYPE_EXE,
	need_AES=False,
	includedirs=includedirs_7za,
	defines=[ "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_Client7z.files_c,
	files_cpp=file_Client7z.files_cpp,
	cmake_end='''

find_library(DL_LIB dl)

link_directories(${DL_LIB_PATH})

IF(APPLE)
   TARGET_LINK_LIBRARIES(Client7z ${COREFOUNDATION_LIBRARY} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(Client7z ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''',
android_header=r'''
LOCAL_CFLAGS := -DANDROID_NDK  -fexceptions \
	-DNDEBUG -D_REENTRANT -DENV_UNIX \
	-DEXTERNAL_CODECS \
	-DBREAK_HANDLER \
	-DUNICODE -D_UNICODE -DUNIX_USE_WIN_FILE \
	-I../../../Windows \
	-I../../../Common \
	-I../../../../C \
-I../../../myWindows \
-I../../../ \
-I../../../include_windows
''')

project_P7ZIP=Structure(name="P7ZIP",name2="P7ZIP",
	type=TYPE_EXE,
	need_AES=False,
	includedirs=includedirs_7za,
	defines=[ "LANG", "EXTERNAL_CODECS", "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_P7ZIP.files_c,
	files_cpp=file_P7ZIP.files_cpp,
	cmake_end='''

IF(APPLE)
  add_definitions(-DENV_MACOSX  -D__WXMAC__)
ENDIF(APPLE)

find_package(wxWidgets COMPONENTS core base adv REQUIRED)

find_library(DL_LIB dl)

include( ${wxWidgets_USE_FILE} )

link_directories(${DL_LIB_PATH})

IF(APPLE)
   TARGET_LINK_LIBRARIES(P7ZIP ${COREFOUNDATION_LIBRARY} ${wxWidgets_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(P7ZIP ${wxWidgets_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''')

project_TestUI=Structure(name="TestUI",name2="TestUI",
	type=TYPE_EXE,
	need_AES=False,
	includedirs=includedirs_7za,
	defines=[ "LANG", "EXTERNAL_CODECS", "_FILE_OFFSET_BITS=64", "_LARGEFILE_SOURCE", "_REENTRANT", "ENV_UNIX", "BREAK_HANDLER", "UNICODE", "_UNICODE", "UNIX_USE_WIN_FILE" ],
	files_c=file_TestUI.files_c,
	files_cpp=file_TestUI.files_cpp,
	cmake_end='''

IF(APPLE)
  add_definitions(-DENV_MACOSX  -D__WXMAC__)
ENDIF(APPLE)

find_package(wxWidgets COMPONENTS core base adv REQUIRED)

find_library(DL_LIB dl)

include( ${wxWidgets_USE_FILE} )

link_directories(${DL_LIB_PATH})

IF(APPLE)
   TARGET_LINK_LIBRARIES(TestUI ${COREFOUNDATION_LIBRARY} ${wxWidgets_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT})
ELSE(APPLE)
  IF(HAVE_PTHREADS)
   TARGET_LINK_LIBRARIES(TestUI ${wxWidgets_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT} dl)
  ENDIF(HAVE_PTHREADS)
ENDIF(APPLE)

''')
generate_makefile_list('../CPP/7zip/Bundles/Alone/makefile.list',project_7za)
generate_makefile_list('../CPP/7zip/Bundles/Alone7z/makefile.list',project_7zr)
generate_makefile_list('../CPP/7zip/UI/Console/makefile.list',project_7z)
generate_makefile_list('../CPP/7zip/Bundles/Format7zFree/makefile.list',project_Format7zFree)
generate_makefile_list('../CPP/7zip/Compress/Rar/makefile.list',project_Codecs_Rar,'../../../../bin/Codecs')
generate_makefile_list('../CPP/7zip/Compress/Lzham/makefile.list',project_Codecs_Lzham,'../../../../bin/Codecs')
generate_makefile_list('../CPP/7zip/Compress/ZStd/makefile.list',project_Codecs_ZStd,'../../../../bin/Codecs')
generate_makefile_list('../CPP/7zip/Bundles/SFXCon/makefile.list',project_7zCon_sfx)
generate_makefile_list('../CPP/7zip/UI/GUI/makefile.list',project_7zG)
generate_makefile_list('../CPP/7zip/UI/FileManager/makefile.list',project_7zFM)
generate_makefile_list('../CPP/7zip/Bundles/LzmaCon/makefile.list',project_LzmaCon)
generate_makefile_list('../CPP/7zip/UI/Client7z/makefile.list',project_Client7z)
generate_makefile_list('../CPP/7zip/UI/P7ZIP/makefile.list',project_P7ZIP)
generate_makefile_list('../CPP/7zip/TEST/TestUI/makefile.list',project_TestUI)

generate_pro('../CPP/7zip/QMAKE/7za/7za.pro',project_7za)
generate_pro('../CPP/7zip/QMAKE/7zr/7zr.pro',project_7zr)
generate_pro('../CPP/7zip/QMAKE/7z_/7z_.pro',project_7z)
generate_pro('../CPP/7zip/QMAKE/Format7zFree/Format7zFree.pro',project_Format7zFree)
generate_pro('../CPP/7zip/QMAKE/Rar/Rar.pro',project_Codecs_Rar)
generate_pro('../CPP/7zip/QMAKE/Lzham/Lzham.pro',project_Codecs_Lzham)

generate_premake4('../CPP/7zip/PREMAKE/premake4.lua',project_7za)

generate_cmake('../CPP/7zip/CMAKE/7za/CMakeLists.txt',project_7za)
generate_cmake('../CPP/7zip/CMAKE/7z_/CMakeLists.txt',project_7z)
generate_cmake('../CPP/7zip/CMAKE/7zG/CMakeLists.txt',project_7zG)
generate_cmake('../CPP/7zip/CMAKE/7zFM/CMakeLists.txt',project_7zFM)
generate_cmake('../CPP/7zip/CMAKE/7zr/CMakeLists.txt',project_7zr)
generate_cmake('../CPP/7zip/CMAKE/Format7zFree/CMakeLists.txt',project_Format7zFree)


generate_android_mk('../CPP/ANDROID/7za/jni/Android.mk',project_7za)
generate_android_mk('../CPP/ANDROID/7zr/jni/Android.mk',project_7zr)
generate_android_mk('../CPP/ANDROID/7z/jni/Android.mk',project_7z)
generate_android_mk('../CPP/ANDROID/Format7zFree/jni/Android.mk',project_Format7zFree)
generate_android_mk('../CPP/ANDROID/Lzham/jni/Android.mk',project_Codecs_Lzham)


#FIXME:7zr-CPP/7zip/Bundles/Alone7z


