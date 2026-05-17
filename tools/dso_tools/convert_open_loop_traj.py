import csv
import os

parent_path = os.getenv("PARENT_PATH")
pose_file = (
    parent_path + "/viba_input/dso_output/poses.txt"
)  # From formatted map directory
vel_file = parent_path + "/viba_input/dso_output/viba_vel.txt"  # From result directory
imu_file = parent_path + "/viba_input/dso_output/imu.txt"  # From raw data directory
output_file = parent_path + "/viba_input/open_loop_trajectory.csv"

vel_dict = {}
with open(vel_file, "r") as f:
    for line in f:
        if line.startswith("#") or line.strip() == "":
            continue

        parts = line.strip().split()
        ts = int(parts[0])
        vx, vy, vz = map(float, parts[1:4])
        wx, wy, wz = map(float, parts[4:7])
        # gx, gy, gz = map(float, parts[7:10])
        gx, gy, gz = 0, 0, -9.8082
        vel_dict[ts] = (vx, vy, vz, wx, wy, wz, gx, gy, gz)

imu_dict = {}
with open(imu_file, "r") as f:
    for line in f:
        if line.startswith("#") or line.strip() == "":
            continue

        parts = line.strip().split()
        ts = int(parts[0])
        wx, wy, wz = map(float, parts[1:4])
        imu_dict[ts] = (wx, wy, wz)

with open(pose_file, "r") as fin, open(output_file, "w", newline="") as fout:
    writer = csv.writer(fout)

    # Header exactly as MPS expects
    writer.writerow(
        [
            "tracking_timestamp_us",
            "utc_timestamp_ns",
            "session_uid",
            "tx_odometry_device",
            "ty_odometry_device",
            "tz_odometry_device",
            "qx_odometry_device",
            "qy_odometry_device",
            "qz_odometry_device",
            "qw_odometry_device",
            "device_linear_velocity_x_odometry",
            "device_linear_velocity_y_odometry",
            "device_linear_velocity_z_odometry",
            "angular_velocity_x_device",
            "angular_velocity_y_device",
            "angular_velocity_z_device",
            "gravity_x_odometry",
            "gravity_y_odometry",
            "gravity_z_odometry",
            "quality_score",
        ]
    )

    for line in fin:
        if line.startswith("#") or line.strip() == "":
            continue

        parts = line.strip().split()

        # Pose parsing
        timestamp_ns = int(parts[0])
        tx, ty, tz = map(float, parts[1:4])
        qw, qx, qy, qz = map(float, parts[4:8])
        tracking_timestamp_us = int(timestamp_ns / 1000)
        utc_timestamp_ns = -1
        session_uid = "3edc41cb-c537-e828-8bf9-403e7c3afdfd"

        # Vel parsing
        if timestamp_ns in vel_dict:
            vx, vy, vz, wx, wy, wz, gx, gy, gz = vel_dict[timestamp_ns]
            vel = [vx, vy, vz]
            ang_vel = [wx, wy, wz]
            gravity = [gx, gy, gz]
            quality = 1.0
        else:
            vel = [0.0, 0.0, 0.0]
            ang_vel = [0.0, 0.0, 0.0]
            gravity = [0.0, 0.0, -9.81]
            quality = 0.5

        # IMU parsing
        if timestamp_ns in imu_dict:
            wx, wy, wz = imu_dict[timestamp_ns]
            ang_vel = [wx, wy, wz]

        writer.writerow(
            [
                tracking_timestamp_us,
                utc_timestamp_ns,
                session_uid,
                tx,
                ty,
                tz,
                qx,
                qy,
                qz,
                qw,
                *vel,
                *ang_vel,
                *gravity,
                quality,
            ]
        )

print("Done: open_loop_trajectory.csv generated")
