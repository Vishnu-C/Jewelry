cmake_minimum_required(VERSION 2.8.2)

project(ringNamer)

# define install prefix
set(CMAKE_INSTALL_PREFIX ${CMAKE_CURRENT_SOURCE_DIR})

# define namer dir and src dir
set(NAMER_DIR ${CMAKE_CURRENT_SOURCE_DIR})

# c++ flags
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -DNDEBUG -lstdc++fs -std=c++11 -fopenmp")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -Wall -pedantic -O0 -Wextra -lstdc++fs -std=c++11 -fopenmp")
# add_compile_options(-std=c++11)

# VTK
find_package(VTK REQUIRED NO_MODULE)

if ( VTK_FOUND )
  message(STATUS "The VTK is " ${VTK_VERSION})
  message(STATUS "The VTK libraries " ${VTK_LIBRARIES})
  include(${VTK_USE_FILE})
else()
  message(STATUS "This program requires the CGAL library, and will not be compiled.")
endif()

#################################
## OCE include and lib location #
#################################
#set(OCE_REQUIRED_LIBS TKernel TKMath TKBRep TKG2d TKG3d TKMeshVS TKPrim TKGeomBase TKGeomAlgo TKTopAlgo TKShHealing)
set(OCE_REQUIRED_LIBS
TKernel
TKMath
TKG2d
TKG3d
TKGeomBase
TKBRep
TKGeomAlgo
TKTopAlgo
TKPrim
TKBO
TKHLR
TKMesh
TKShHealing
TKXMesh
TKBool
TKFillet
TKFeat
TKOffset
TKService
TKV3d
TKOpenGl
TKMeshVS
TKNIS
TKVoxel
TKIVtk
TKCDF
PTKernel
TKLCAF
FWOSPlugin
TKPShape
TKBinL
TKXmlL
TKPLCAF
TKTObj
TKShapeSchema
TKStdLSchema
TKCAF
TKBin
TKXml
TKPCAF
TKBinTObj
TKXmlTObj
TKStdSchema
TKSTL
TKXSBase
TKSTEPBase
TKIGES 
TKSTEPAttr
TKSTEP209
TKSTEP
TKVRML
TKXCAF
TKXCAFSchema
TKXmlXCAF
TKBinXCAF
TKXDEIGES
TKXDESTEP
TKDraw
TKTopTest
TKViewerTest
TKXSDRAW
TKDCAF
TKXDEDRAW
TKTObjDRAW)

find_package(OCE
    COMPONENTS ${OCE_REQUIRED_LIBS}
    CONFIG)
if(OCE_FOUND)
    message(STATUS "OpenCASCADE Community Edition found.")
    include_directories(${OCE_INCLUDE_DIRS})
    set(OCE_LIBRARIES ${OCE_REQUIRED_LIBS})
    message(STATUS "The OCE libraries " ${OCE_LIBRARIES})
else()
    set( OCE_INCLUDE_PATH /usr/local/include/oce CACHE
        PATH "OCE headers location" )
    set( OCE_LIB_PATH /usr/local/lib CACHE
        PATH "OCE libraries location" )
    set(OCE_LIBRARIES TKernel TKMath TKBRep TKG2d TKG3d TKMeshVS TKPrim TKGeomBase TKGeomAlgo TKTopAlgo TKShHealing)
    # Tells CMake where are the required headers
    include_directories(${OCE_INCLUDE_PATH})
    LINK_DIRECTORIES(${OCE_LIB_PATH})
endif()


find_package(MPI)
include_directories(SYSTEM ${MPI_INCLUDE_PATH})

find_package(OpenMP REQUIRED) # Find the package

# namer
include_directories(${NAMER_DIR}/include)

file(GLOB NAMER_srcs 
    "${NAMER_DIR}/src/RingNamer.cpp" 
    )

add_executable(ringNamer ${NAMER_srcs})
target_link_libraries(ringNamer ${VTK_LIBRARIES})
target_link_libraries(ringNamer ${OCE_LIBRARIES})
target_link_libraries(ringNamer ${MPI_C_LIBRARIES})
target_link_libraries(ringNamer ${OpenMP_CXX_LIBRARIES})