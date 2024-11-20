from scipy.spatial.transform import Rotation as R

import numpy as np

import argparse
import csv
import sys
import os

root_path = os.path.abspath("/esim_ws/src")

# Parse arguments
parser = argparse.ArgumentParser(description="Generate a circular camera trajectory")
parser.add_argument(
    "-a",
    "--amplitude",
    type=float,
    default=0.3,
    help="Amplitude of the circular trajectory (in mm)",
)
parser.add_argument(
    "-f",
    "--frequency",
    type=float,
    default=100,
    help="Frequency of the circular trajectory (in Hz)",
)
parser.add_argument(
    "-o",
    "--output_file",
    type=str,
    default=os.path.join(
        root_path,
        "event_camera_simulator/imp/imp_opengl_renderer/resources/objects/",
        "trajectory.csv",
    ),
    help="Output file path",
)
parser.add_argument(
    "-cx",
    "--center_x",
    type=float,
    default=0.0,
    help="X coordinate of the center of the object (in mm)",
)
parser.add_argument(
    "-cy",
    "--center_y",
    type=float,
    default=0.0,
    help="Y coordinate of the center of the object (in mm)",
)
parser.add_argument(
    "-cz",
    "--center_z",
    type=float,
    default=0.0,
    help="Z coordinate of the center of the object (in mm)",
)
parser.add_argument(
    "-ax", "--axis_x", type=float, help="X coordinate of the camera (in mm)"
)
parser.add_argument(
    "-ay", "--axis_y", type=float, help="Y coordinate of the camera (in mm)"
)
parser.add_argument(
    "-az", "--axis_z", type=float, help="Z coordinate of the camera (in mm)"
)
parser.add_argument(
    "-d",
    "--duration",
    type=float,
    default=100,
    help="Duration of the trajectory (in s)",
)
parser.add_argument(
    "-sr",
    "--sampling_rate",
    type=float,
    default=20,
    help="Sampling rate of the trajectory",
)
args = parser.parse_args()


def generate_camera_trajectory(
    amplitude,
    frequency,
    ax,
    ay,
    az,
    cx=0,
    cy=0,
    cz=0,
    duration=10,
    sampling_rate=100,
    output_file="trajectory.csv",
):
    # Parameters
    omega = 2 * np.pi * frequency  # Angular velocity
    center = np.array([ax, ay, az])
    target = np.array([cx, cy, cz])

    # Compute the rotation axis (unit vector from center to target)
    rotation_axis = target - center
    rotation_axis /= np.linalg.norm(rotation_axis)  # Normalize

    # Compute two orthogonal vectors to form a plane
    if np.allclose(rotation_axis, [1, 0, 0]):  # Special case: if aligned with x-axis
        orthogonal1 = np.array([0, 1, 0])
    else:
        orthogonal1 = np.cross(rotation_axis, [1, 0, 0])
    orthogonal1 /= np.linalg.norm(orthogonal1)  # Normalize

    orthogonal2 = np.cross(rotation_axis, orthogonal1)  # Ensure orthogonality
    orthogonal2 /= np.linalg.norm(orthogonal2)

    # Time steps
    t = np.linspace(0, duration, int(duration * sampling_rate))

    # Generate trajectory along the circular path
    x = center[0] + amplitude * (
        np.cos(omega * t) * orthogonal1[0] + np.sin(omega * t) * orthogonal2[0]
    )
    y = center[1] + amplitude * (
        np.cos(omega * t) * orthogonal1[1] + np.sin(omega * t) * orthogonal2[1]
    )
    z = center[2] + amplitude * (
        np.cos(omega * t) * orthogonal1[2] + np.sin(omega * t) * orthogonal2[2]
    )

    positions = np.vstack((x, y, z)).T  # Camera positions

    # Quaternion calculations for orientation
    orientations = []
    for pos in positions:
        direction = target - pos  # Direction to the target
        direction /= np.linalg.norm(direction)  # Normalize direction vector

        # Define the camera's "up" vector
        up = np.array([0, 0, 1]) if np.abs(direction[2]) < 1 else np.array([0, 1, 0])

        # Create rotation matrix to align the camera
        z_axis = direction
        x_axis = np.cross(up, z_axis)
        x_axis /= np.linalg.norm(x_axis)
        y_axis = np.cross(z_axis, x_axis)

        rot_matrix = np.column_stack((x_axis, y_axis, z_axis))
        quaternion = R.from_matrix(
            rot_matrix
        ).as_quat()  # Convert to quaternion (qx, qy, qz, qw)
        orientations.append(quaternion)

    orientations = np.array(orientations)

    # Save to CSV
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["# timestamp", " x", " y", " z", " qx", " qy", " qz", " qw"])
        for i, timestamp in enumerate(t):
            writer.writerow([timestamp * 1e7, x[i], y[i], z[i], *orientations[i]])


if __name__ == "__main__":
    generate_camera_trajectory(
        args.amplitude,
        args.frequency,
        args.axis_x,
        args.axis_y,
        args.axis_z,
        args.center_x,
        args.center_y,
        args.center_z,
        duration=args.duration,
        sampling_rate=args.sampling_rate,
        output_file=args.output_file,
    )
