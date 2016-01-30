INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_TF tf)

FIND_PATH(
    TF_INCLUDE_DIRS
    NAMES tf/api.h
    HINTS $ENV{TF_DIR}/include
        ${PC_TF_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    TF_LIBRARIES
    NAMES gnuradio-tf
    HINTS $ENV{TF_DIR}/lib
        ${PC_TF_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(TF DEFAULT_MSG TF_LIBRARIES TF_INCLUDE_DIRS)
MARK_AS_ADVANCED(TF_LIBRARIES TF_INCLUDE_DIRS)

