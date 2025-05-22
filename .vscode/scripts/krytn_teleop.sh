
#!/bin/bash

# Get the directory of the current script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)" # Go up two levels to the workspace root

# Build the workspace first using the dedicated build script
echo "--- Building workspace ---"
if ! bash "${SCRIPT_DIR}/build.sh"; then
    echo "Build script failed. Exiting."
    exit 1
fi
echo "--- Build finished ---"

# Source the local workspace
echo "--- Sourcing workspace ---"
# Source the main ROS 2 setup if not already in bashrc (important for a clean environment)
if [ -f /opt/ros/${ROS_DISTRO}/setup.bash ]; then
    source /opt/ros/${ROS_DISTRO}/setup.bash
    echo "Sourced /opt/ros/${ROS_DISTRO}/setup.bash"
else
    echo "Warning: Global ROS 2 setup script not found for ROS_DISTRO=${ROS_DISTRO}"
fi

# Source the local workspace overlay
if [ -f "${WORKSPACE_DIR}/install/setup.bash" ]; then
    source "${WORKSPACE_DIR}/install/setup.bash"
    echo "Sourced ${WORKSPACE_DIR}/install/setup.bash"
else
    echo "Error: Local workspace setup.bash not found in ${WORKSPACE_DIR}/install/. Build first. Exiting."
    exit 1
fi
echo "--- Workspace sourced ---"

# Verify OpenGL renderer with vglrun before launching anything GPU intensive
echo "Verifying OpenGL renderer with vglrun..."
if command -v vglrun &> /dev/null; then
    vglrun_path=$(command -v vglrun)
    echo "vglrun found at: ${vglrun_path}"
    VGL_OUTPUT=$(vglrun glxinfo -B 2>&1)
    RENDERER_STRING=$(echo "${VGL_OUTPUT}" | grep "OpenGL renderer string" | sed 's/.*OpenGL renderer string: //')
    if [[ "${RENDERER_STRING}" == *"NVIDIA"* || "${RENDERER_STRING}" == *"Quadro"* || "${RENDERER_STRING}" == *"GeForce"* || "${RENDERER_STRING}" == *"Tesla"* ]]; then
        echo "SUCCESS: vglrun is using NVIDIA GPU: ${RENDERER_STRING}"
    elif [[ -z "${RENDERER_STRING}" ]]; then
        echo "WARNING: Could not determine OpenGL renderer string via vglrun. Output was:"
        echo "${VGL_OUTPUT}"
        echo "Proceeding, but GPU acceleration might not be active."
    else
        echo "WARNING: vglrun is using CPU-based rendering (Mesa/llvmpipe): ${RENDERER_STRING}"
        echo "Proceeding, but GPU acceleration might not be active."
    fi
else
    echo "Error: vglrun not found. Cannot ensure GPU acceleration. Please install VirtualGL."
    echo "Proceeding without vglrun. GUI performance may be affected."
    # Optionally exit here if vglrun is mandatory:
    # exit 1
fi

# Launch the teleop application
# The actual ROS 2 launch command will be prefixed with vglrun by the launch file if needed for specific nodes,
# or we can prefix the entire launch command here if all GUI elements need it.
# For Gazebo and RViz, it's common to vglrun them individually in the launch file.
# However, your krytn_teleop.sh calls gazebo.launch.py, which launches Gazebo and RQT.
# We will modify gazebo.launch.py to use vglrun for Gazebo and RQT.
# This script ensures the environment is set up for vglrun to work.

echo "Launching Krytn Teleop (gazebo.launch.py)..."
# The launch file will handle vglrun for specific GUI nodes
ros2 launch krytn gazebo.launch.py
# If you wanted to vglrun the *entire* launch process (less common, can have side effects):
# vglrun ros2 launch krytn gazebo.launch.py

echo "Krytn Teleop script finished."