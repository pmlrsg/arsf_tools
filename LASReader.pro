#-------------------------------------------------
#
# Project created by QtCreator 2014-09-08T10:35:11
#
#-------------------------------------------------

QT       += core

QT       -= gui

TARGET = LASReader
CONFIG   += console
CONFIG   -= app_bundle

TEMPLATE = app


SOURCES += main.cpp \
    Las1_3_handler.cpp \
    Pulse.cpp \
    PulseManager.cpp

HEADERS += \
    Types.h \
    Las1_3_handler.h \
    Pulse.h \
    PulseManager.h


INCLUDEPATH += "/users/rsg/mmi/gmtl-0.6.1/build/include/gmtl-0.6.1/"
CONFIG += c++11


QMAKE_CXXFLAGS += -std=gnu++0x
QMAKE_CXXFLAGS += -std=c++0x

