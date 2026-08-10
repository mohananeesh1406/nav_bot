
import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'my_robot_description'

    pkg_share = get_package_share_directory(package_name)

    urdf_file = os.path.join(
        pkg_share,
        'urdf',
        'robot.urdf'
    )

    # Read URDF
    with open(urdf_file, 'r') as file:
        robot_description = file.read()

    # Start Ignition Gazebo 6
    gazebo = ExecuteProcess(
        cmd=[
            'ign',
            'gazebo',
            '-r',
            'empty.sdf'
        ],
        output='screen'
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {
                'robot_description': robot_description
            }
        ]
    )

    joint_state_publisher_gui = Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui'
        )

    

    # Spawn URDF into Ignition Gazebo
    spawn_robot = ExecuteProcess(
        cmd=[
            'ign',
            'service',
            '-s',
            '/world/empty/create',
            '--reqtype',
            'ignition.msgs.EntityFactory',
            '--reptype',
            'ignition.msgs.Boolean',
            '--timeout',
            '5000',
            '--req',
            'sdf_filename: "' + urdf_file + '", '
            'name: "my_robot"'
        ],
        output='screen'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        robot_state_publisher,
        joint_state_publisher_gui,
        spawn_robot,
        rviz
    ])
