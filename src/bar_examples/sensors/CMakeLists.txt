
cmake_minimum_required(VERSION 3.8)
project(sensors)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_auto REQUIRED)

ament_auto_find_build_dependencies()

# This installs the contents of the 'realsense_d435' source directory
# (e.g., src/sensors/realsense_d435/)
# into 'install/sensors/share/sensors/realsense_d435/'
install(
    DIRECTORY realsense_d435/
    DESTINATION share/${PROJECT_NAME}/realsense_d435
)

# This installs the contents of the 'lidar_2d' source directory
# (e.g., src/sensors/lidar_2d/, which should contain an 'urdf' subfolder)
# into 'install/sensors/share/sensors/lidar_2d/'
install(
    DIRECTORY lidar_2d/
    DESTINATION share/${PROJECT_NAME}/lidar_2d
)

ament_package()