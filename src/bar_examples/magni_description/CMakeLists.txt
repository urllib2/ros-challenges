
cmake_minimum_required(VERSION 3.8)
project(magni_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_auto REQUIRED)

ament_auto_find_build_dependencies()

# This installs the contents of the 'urdf', 'meshes', and 'materials'
# directories from your source (e.g., src/magni_description/urdf/)
# into the install space (e.g., install/magni_description/share/magni_description/urdf/).
ament_auto_package(
  INSTALL_TO_SHARE
    urdf
    meshes
    materials # Add this only if you have a 'materials' directory in src/magni_description
              # containing texture files or material scripts for Gazebo/RViz.
              # If not, remove 'materials' from this list.
)

# The problematic install(DIRECTORY) and install(CODE) for symlinks are removed.
# package:// paths used in URDFs should resolve correctly with the above.