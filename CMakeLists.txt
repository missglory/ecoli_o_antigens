cmake_minimum_required(VERSION 3.10)
project(oantigens)

set(GEDLIB_ROOT ${CMAKE_SOURCE_DIR}/gedlib)
message("gedlib": ${GEDLIB_ROOT})

find_package(Boost 1.69 REQUIRED COMPONENTS thread chrono system)

include_directories(    
    ${GEDLIB_ROOT} 
    ${Boost_INCLUDE_DIR}
    ${GEDLIB_ROOT}/ext/eigen.3.3.4/Eigen
    ${GEDLIB_ROOT}/ext/nomad.3.8.1/src
    ${GEDLIB_ROOT}/ext/nomad.3.8.1/ext/sgtelib/src
    ${GEDLIB_ROOT}/ext/lsape.5/include
    ${GEDLIB_ROOT}/ext/libsvm.3.22
    ${GEDLIB_ROOT}/ext/fann.2.2.0/include
)

add_executable(oantigens main.cpp)

find_library(NOMAD_LIB libnomad.so
    PATHS ${GEDLIB_ROOT}/ext/nomad.3.8.1/lib)
find_library(FANN_LIB libdoublefann.so.2
    PATHS ${GEDLIB_ROOT}/ext/fann.2.2.0/lib)
find_library(SVM_LIB libsvm.so
    PATHS ${GEDLIB_ROOT}/ext/libsvm.3.22)
find_package(Threads REQUIRED)

message("thread lib: " ${CMAKE_THREAD_LIBS_INIT})
target_link_libraries(oantigens
    # ${GEDLIB_ROOT}/ext/fann.2.2.0/lib/libdoublefann.2.dylib
    ${FANN_LIB}
    ${SVM_LIB}
    ${NOMAD_LIB}
    ${CMAKE_THREAD_LIBS_INIT}
    ${Boost_LIBRARIES}
)


