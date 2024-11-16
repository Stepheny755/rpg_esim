FROM osrf/ros:noetic-desktop-full

# define/create repository path
ARG REPO_PATH="/esim_ws/src"
RUN mkdir -p "${REPO_PATH}"
WORKDIR "${REPO_PATH}"

RUN apt-get update && apt-get install -y \
curl \
wget \
ros-noetic-pcl-ros \
libproj-dev \
libglfw3 \
libglfw3-dev \
libglm-dev \
python3-catkin-tools \
python3-vcstool \
git \
libtool \
libtool-bin

# run esim install
RUN mkdir -p ~/sim_ws/src && mkdir -p ~/sim_ws/logs && cd ~/sim_ws
COPY . ${REPO_PATH}
RUN vcs import < dependencies.yaml
WORKDIR /esim_ws
RUN catkin init && catkin config --extend /opt/ros/noetic --cmake-args -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS=-Wno-int-in-bool-context && catkin build esim_ros

# setup entrypoint
CMD ["./src/run.sh"]