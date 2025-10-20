cmake_minimum_required(VERSION 3.20)
project(volumetric_display)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(APPLE)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-deprecated-declarations")
endif()

include(FetchContent)

# System packages
find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)
find_package(GLEW REQUIRED)
find_package(glm REQUIRED)
find_package(absl REQUIRED)

# For Boost, just find the headers and link manually with system libs
find_package(Boost REQUIRED)

# nlohmann_json via HTTPS (header-only, fast download)
FetchContent_Declare(
    nlohmann_json
    URL https://github.com/nlohmann/json/archive/refs/tags/v3.11.3.zip
)
set(JSON_BuildTests OFF CACHE INTERNAL "")
FetchContent_MakeAvailable(nlohmann_json)

# Copy icon.png to build directory if it exists
if(EXISTS "${CMAKE_SOURCE_DIR}/resources/icon.png")
    configure_file(
        "${CMAKE_SOURCE_DIR}/resources/icon.png"
        "${CMAKE_BINARY_DIR}/resources/icon.png"
        COPYONLY
    )
endif()

# Executable with icon support
add_executable(simulator 
    main.cpp
    resources/icon_cmake.cpp  # CMake-specific version
    resources/icon_helper.h
    resources/icon.h
)

# Add platform-specific icon helper
if(APPLE)
    target_sources(simulator PRIVATE resources/icon_helper_osx.cpp)
    # Tell CMake to treat this .cpp file as Objective-C++
    set_source_files_properties(resources/icon_helper_osx.cpp PROPERTIES
        COMPILE_FLAGS "-x objective-c++"
    )
    target_link_libraries(simulator PRIVATE "-framework Cocoa")
else()
    target_sources(simulator PRIVATE resources/icon_helper_linux.cpp)
endif()

target_link_libraries(simulator PRIVATE volumetric_display absl::flags_parse absl::log_initialize)
target_include_directories(simulator PRIVATE .)
add_library(volumetric_display
    VolumetricDisplay.cpp
    VolumetricDisplay.h
    DisplayConfig.h
    color_correction.h
)

target_include_directories(volumetric_display PUBLIC . resources)

target_link_libraries(volumetric_display PUBLIC
    OpenGL::GL
    glfw
    GLEW::GLEW
    glm::glm
    Boost::headers
    nlohmann_json::nlohmann_json
    absl::log
    absl::flags
)

if(APPLE)
    target_link_libraries(volumetric_display PUBLIC "-framework OpenGL" "-framework Cocoa")
endif()