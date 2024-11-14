
FROM osrf/ros:noetic-desktop-full

ENV REPO_PATH /esim_ws
RUN mkdir -p ${REPO_PATH}

RUN apt-get update && apt-get install -y \
    curl \
    wget \ 
    gnutls-bin \
    git \
    ros-noetic-pcl-ros \
    libproj-dev \
    libglfw3 \
    libglfw3-dev \
    libglm-dev \
    python3-catkin-tools \
    python3-vcstool

# run esim install
RUN mkdir -p ${REPO_PATH}/src && mkdir -p ${REPO_PATH}/logs && cd ${REPO_PATH}
COPY . ${REPO_PATH}/src
WORKDIR ${REPO_PATH}/src
RUN vcs import < ${REPO_PATH}/src/dependencies.yaml
WORKDIR ${REPO_PATH}
RUN catkin init && catkin config --extend /opt/ros/noetic --cmake-args -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS=-Wno-int-in-bool-context && catkin build esim_ros
# RUN catkin build esim_ros