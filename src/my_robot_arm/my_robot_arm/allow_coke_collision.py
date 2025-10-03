#!/usr/bin/env python3

import rclpy
from rclpy.callback_groups import ReentrantCallbackGroup
from threading import Thread
from pymoveit2 import MoveIt2

def main():
    rclpy.init()
    node = rclpy.create_node(node_name="my_robot_arm_moveit_controller")
    logger = node.get_logger()
    
    callback_group = ReentrantCallbackGroup()

    moveit2 = MoveIt2(node=node, 
                      joint_names=['ur5_shoulder_pan_joint', 'ur5_shoulder_lift_joint',
                                   'ur5_elbow_joint','ur5_wrist_1_joint',
                                   'ur5_wrist_2_joint','ur5_wrist_3_joint'],
                      base_link_name='ur5_base_link',
                      end_effector_name='gripper',
                      group_name='arm',
                      callback_group=callback_group                      )

    # Spin the node in background thread(s) and wait a bit for initialization
    executor = rclpy.executors.MultiThreadedExecutor(2)
    executor.add_node(node)
    executor_thread = Thread(target=executor.spin, daemon=True, args=())
    executor_thread.start()
    node.create_rate(3.0).sleep()

    logger.info("Create collision box ")

    obj_id = 'Coke_Collision_Box'
    pos = [0.22, -0.35, -0.55] # adjusted manually
    quatr_xyzw = [0, 0, 0, 1]
 

    moveit2.add_collision_cylinder(
        obj_id, 
        height=0.14,
        radius=0.03,
        position=pos, 
        quat_xyzw=quatr_xyzw,
        frame_id='world',
    )

    logger.info("Allow collisions")
    moveit2.allow_collisions(obj_id, True)

    logger.info("Shutdown")
    rclpy.shutdown()
    logger.info("Close thread")
    executor_thread.join()

if __name__ == '__main__':
    main()