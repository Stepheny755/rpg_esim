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
libtool-bin \
tmux \
vim 

# copy files
RUN mkdir -p ~/sim_ws/src && mkdir -p ~/sim_ws/logs && cd ~/sim_ws
COPY event_camera_simulator ${REPO_PATH}/event_camera_simulator
COPY dependencies.yaml ${REPO_PATH}

# fix rpg_esim issues
# issue: https://github.com/uzh-rpg/rpg_esim/issues/1
RUN find ${REPO_PATH}/event_camera_simulator/ -type f -exec sed -i 's/\<const int num_samples = 16\>/const int num_samples = 4/g' {} \;

# run esim install
RUN vcs import < dependencies.yaml
WORKDIR /esim_ws
RUN catkin init && catkin config --extend /opt/ros/noetic --cmake-args -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_FLAGS=-Wno-int-in-bool-context && catkin build esim_ros

# bashrc
RUN echo "alias setb='source /esim_ws/devel/setup.bash'" >> ~/.bashrc

# setup config
COPY sim/*.conf "${REPO_PATH}/event_camera_simulator/esim_ros/cfg"

# use python3 
RUN find ${REPO_PATH} -type f -exec sed -i 's/\#\!\/usr\/bin\/env \<python\>/\#\!\/usr\/bin\/env python3/g' {} \;

EXPOSE 9000

# apply patches
# issue: https://github.com/uzh-rpg/rpg_esim/issues/97
COPY sim/patches/esim.perspective "${REPO_PATH}/event_camera_simulator/esim_visualization/cfg"