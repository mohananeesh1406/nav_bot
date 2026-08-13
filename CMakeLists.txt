cmake_minimum_required(VERSION 3.8)
project(my_robot_description)

find_package(ament_cmake REQUIRED)
find_package(rclpy REQUIRED)
find_package(std_msgs REQUIRED)

# Install URDF, launch, and config files
install(
  DIRECTORY
    urdf
    launch
    config
    worlds
  DESTINATION share/${PROJECT_NAME}
)

ament_package()