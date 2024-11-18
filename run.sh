#!/bin/bash

# source the ROS environment
source /esim_ws/devel/setup.bash

# start roscore in another process
(source /esim_ws/devel/setup.bash && roscore &)

# wait for roscore to start
sleep 10

(source /esim_ws/devel/setup.bash && roscd esim_visualization/ && rviz -d cfg/esim.rviz)

roslaunch esim_ros esim.launch config:=cfg/example.conf
