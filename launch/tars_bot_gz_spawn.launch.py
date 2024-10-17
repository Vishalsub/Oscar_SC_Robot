from os.path import join
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    tars_amr_path = get_package_share_directory("tars_amr_sim")
    position_x = LaunchConfiguration("position_x")
    position_y = LaunchConfiguration("position_y")


    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        name="robot_state_publisher",
        parameters=[{
            'robot_description': Command([
                'xacro ', join(tars_amr_path, 'description/robot.urdf.xacro'),
                ' sim_gz:=', "true"
            ])
        }],
        remappings=[('/joint_states', '/joint_states')]
    )

    gz_spawn_entity = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic", "/robot_description",
            "-name", "my_bot",
            "-allow_renaming", "true",
            "-z", "0.28",
            "-x", position_x,
            "-y", position_y,

        ]
    )

    gz_ros2_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist",
            "/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock",
            "/odom@nav_msgs/msg/Odometry[ignition.msgs.Odometry",
            "/tf@tf2_msgs/msg/TFMessage[ignition.msgs.Pose_V",
            "/world/default/model/my_bot/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model"
        ],
        remappings=[
            ('/world/default/model/my_bot/joint_state', '/joint_states'),
            ('/cmd_vel', 'tars_amr_sim/cmd_vel'),
        ]
    )

    transform_publisher = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "--x", "0.0",
            "--y", "0.0",
            "--z", "0.0",
            "--yaw", "0.0",
            "--pitch", "0.0",
            "--roll", "0.0",
            "base_link", "world"  # Specify the parent and child frame IDs
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument("position_x", default_value="0.0"),
        DeclareLaunchArgument("position_y", default_value="0.0"),
        robot_state_publisher,
        gz_spawn_entity,
        transform_publisher,
        gz_ros2_bridge,
    ])