
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, LogInfo
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from os.path import join
from launch.substitutions import LaunchConfiguration, Command
from launch.actions import DeclareLaunchArgument

def generate_launch_description():

    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_krytn_description = get_package_share_directory('krytn') # Assuming krytn for robot description
    pkg_krytn_launch_utils = get_package_share_directory('krytn') # For other launch files if needed

    # Common D.A.V.E. params
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    # Gazebo Sim
    # Note: The world path is now relative to krytn package, but gamecity.sdf is in gamecity package.
    # This assumes gamecity.sdf has been copied or is accessible via GAZEBO_RESOURCE_PATH
    # For robust behavior, let's use the gamecity package explicitly for the world.
    pkg_gamecity_description = get_package_share_directory('gamecity')
    world_file = LaunchConfiguration('world_file', default=join(pkg_gamecity_description, 'worlds', 'gamecity.sdf'))
    
    # Declare launch arguments that can be passed via command line
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_world_cmd = DeclareLaunchArgument(
        'world_file',
        default_value=join(pkg_gamecity_description, 'worlds', 'gamecity.sdf'),
        description='Full path to the Gazebo world file to load')

    # Log the vglrun status (can be checked from the script already)
    log_vglrun_status = LogInfo(msg="Attempting to launch Gazebo and RQT with vglrun where applicable.")

    # Gazebo launch
    # We will add 'vglrun' to the gz_args if needed, or prefix the IncludeLaunchDescription
    # Prefixing the IncludeLaunchDescription is often cleaner for the whole sim.
    # However, gz_sim.launch.py itself launches the 'gz sim' process.
    # The most direct way for Gazebo server (gz sim -s) is usually not vglrun'd.
    # The Gazebo client (gz sim -g) is what needs vglrun.
    # ros_gz_sim's gz_sim.launch.py handles launching server and optionally client.
    # For simplicity and to ensure GUI elements get it, we will try to make sure
    # any GUI launched by gz_sim.launch.py or its children is vglrun'd if possible.
    # The simplest approach for ros_gz applications is often to vglrun the specific ROS nodes that launch GUI.
    
    # The gz_sim.launch.py will launch the Gazebo server.
    # The 'gz_args' are passed to the 'gz sim' command.
    # We usually don't vglrun the server, only client GUI.
    # If gz_sim.launch.py also launches a client GUI (it can with -g), that GUI would benefit.
    # However, most ROS users launch RViz separately.
    gazebo_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r -v4 ', world_file]}.items() # -r to run paused, -v4 for verbosity
    )

    # Robot Description
    xacro_file = join(pkg_krytn_description, 'robot_description', 'krytn.urdf.xacro')
    robot_description_content = Command(['xacro ', xacro_file])

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_content,
                     'use_sim_time': use_sim_time}],
    )

    # Spawn Robot
    spawn_robot_node = Node(
        package='ros_gz_sim',
        executable="create",
        arguments=[
            "-topic", "/robot_description",
            "-name", "krytn",
            "-z", "0.5",
        ],
        output="screen"
    )

    # Bridge
    # Using the bridge arguments from your repo's krytn/launch/gazebo.launch.py
    # as they seemed to be working for bridging in recent logs.
    gz_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            # Clock
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Odometry (DiffDrive an Gz topic or is it from ROS controller?)
            # '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry', # If Gazebo publishes odom directly
            # Lidar
            '/lidar@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan@/gz/krytn_lidar/scan', # Your corrected version
            # Realsense
            '/realsense/image_raw@sensor_msgs/msg/Image[gz.msgs.Image@/gz/krytn_realsense/image',
            '/realsense/depth/image_raw@sensor_msgs/msg/Image[gz.msgs.Image@/gz/krytn_realsense/depth_image',
            '/realsense/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked@/gz/krytn_realsense/points',
            '/realsense/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo@/gz/krytn_realsense/camera_info',
        ],
        output='screen'
    )

    # RQT Robot Steering - This is a GUI tool
    robot_steering = Node(
        package="rqt_robot_steering",
        executable="rqt_robot_steering",
        name="rqt_robot_steering",
        prefix="vglrun", # Add vglrun prefix
        output="screen"
    )

    # Controllers Spawner
    controllers_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=['joint_state_broadcaster', 'diff_drive_base_controller'],
        parameters=[{'use_sim_time': use_sim_time}],
        output="screen",
    )

    # Twist Stamper
    twist_stamper = Node(
        package="twist_stamper",
        executable="twist_stamper.py", # Assuming it's in this package
        name="twist_stamper",
        remappings=[("/cmd_vel_in", "/cmd_vel"),
                       ("/cmd_vel_out",  "/diff_drive_base_controller/cmd_vel")],
        parameters=[{'use_sim_time': use_sim_time}],
        output="screen"
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_world_cmd,
        log_vglrun_status,
        gazebo_sim,
        gz_bridge,
        robot_state_publisher,
        spawn_robot_node,
        controllers_spawner,
        twist_stamper,
        robot_steering, # RQT is now vglrun'd
    ])