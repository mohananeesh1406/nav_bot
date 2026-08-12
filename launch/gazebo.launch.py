import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

from launch.actions import RegisterEventHandler
from launch.event_handlers import OnProcessExit


def generate_launch_description():

    # ---------------------------------------------------------
    # Package paths
    # ---------------------------------------------------------

    pkg_my_robot_description = get_package_share_directory(
        'my_robot_description'
    )

    pkg_ros_gz_sim = get_package_share_directory(
        'ros_gz_sim'
    )

    urdf_file = os.path.join(
        pkg_my_robot_description,
        'urdf',
        'robot.urdf'
    )

    # ---------------------------------------------------------
    # Read URDF
    # ---------------------------------------------------------

    with open(urdf_file, 'r') as f:
        robot_description = f.read()

    # ---------------------------------------------------------
    # Gazebo Fortress
    # ---------------------------------------------------------

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                pkg_ros_gz_sim,
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': '-r empty.sdf'
        }.items()
    )

    # ---------------------------------------------------------
    # Robot State Publisher
    # ---------------------------------------------------------

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

    ros_gz_bridge = Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=[
        '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
    ],
    output='screen',
    )

    # ---------------------------------------------------------
    # Spawn robot into Gazebo
    # ---------------------------------------------------------

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'my_robot',
            '-file', urdf_file,
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.1',
        ],
        output='screen'
    )

    # ---------------------------------------------------------
    # joint state broadcaster
    # ---------------------------------------------------------

    joint_state_broadcaster_spawner = Node(
    package='controller_manager',
    executable='spawner',
    arguments=[
        'joint_state_broadcaster',
        '--controller-manager',
        '/controller_manager',
    ],
    output='screen',
    )

    # ---------------------------------------------------------
    # diff drive controller
    # ---------------------------------------------------------

    diff_drive_controller_spawner = Node(
    package='controller_manager',
    executable='spawner',
    arguments=[
        'diff_drive_controller',
        '--controller-manager',
        '/controller_manager',
    ],
    output='screen',
    )


    start_joint_state_broadcaster = RegisterEventHandler(
        OnProcessExit(
            target_action=spawn_robot,
            on_exit=[
                joint_state_broadcaster_spawner
            ]
        )
    )

    start_diff_drive_controller = RegisterEventHandler(
        OnProcessExit(
            target_action=joint_state_broadcaster_spawner,
            on_exit=[
                diff_drive_controller_spawner
            ]
        )
    )


    # ---------------------------------------------------------
    # Launch everything
    # ---------------------------------------------------------

    return LaunchDescription([
    gazebo,
    ros_gz_bridge,
    robot_state_publisher,
    spawn_robot,
    start_joint_state_broadcaster,
    start_diff_drive_controller,
    ])