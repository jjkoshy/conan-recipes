cmake_minimum_required(VERSION 2.8.11)
project(cmake_wrapper)

include(conanbuildinfo.cmake)
conan_basic_setup()

# TODO: keep only the one which is required
option(protobuf_MODULE_COMPATIBLE "override" ON)
find_program(Protobuf_PROTOC_EXECUTABLE NAMES protoc)
find_program(PROTOBUF_PROTOC_EXECUTABLE NAMES protoc)
set(PROTOBUF_INCLUDE_DIRS "${CONAN_PROTOBUF_ROOT}/include")
set(PROTOBUF_INCLUDE_DIR "${CONAN_PROTOBUF_ROOT}/include")

add_subdirectory(incubator-brpc-0.9.6)
