FROM osrf/ros:jazzy-desktop

WORKDIR /ros2_ws

COPY src/fake_sensors/package.xml src/fake_sensors/

RUN apt-get update && \
    rosdep install --from-paths src --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

COPY src/ src/

RUN . /opt/ros/jazzy/setup.sh && \
    colcon build --packages-select fake_sensors