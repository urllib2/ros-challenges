
    #!/bin/bash

# Source ROS 2 specific environment
ROS_DISTRO_GUESS=$(ls /opt/ros/ | head -n 1)
if [ -z "$ROS_DISTRO_GUESS" ]; then
    echo "Could not guess ROS_DISTRO. Please set it manually or ensure ROS 2 is installed correctly."
    # Consider exiting if ROS_DISTRO is critical: exit 1
else
    echo "Guessed ROS_DISTRO: $ROS_DISTRO_GUESS. Sourcing..."
    source /opt/ros/$ROS_DISTRO_GUESS/setup.bash
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)" # This should correctly be /workspace

# Ensure we are in the workspace root
cd "${WORKSPACE_DIR}"
echo "Current directory for build: $(pwd)"

# Force clean the relevant directories and layout marker BEFORE building
echo "Cleaning build, install, log directories and layout marker..."
rm -rf build/
rm -rf install/
rm -rf log/
rm -f .colcon_install_layout # Explicitly remove the layout marker file
echo "Cleaning done."

# The 'source install/setup.bash' before build is usually not needed
# if you are doing a clean build, as it won't exist.
# If you need to source an underlying workspace, do it before this script.

echo "Starting colcon build..."
# Add --merge-install explicitly if that's the desired layout,
# though it's often the default for modern colcon.
# If you want isolated, remove --merge-install and ensure no old merged markers exist.
# For consistency with ROS 2 best practices, merged is typical.
colcon build --symlink-install --merge-install --event-handlers console_direct+

if [ $? -eq 0 ]; then
    echo "--- Build script finished successfully ---"
else
    echo "--- Build script failed ---"
    exit 1
fi