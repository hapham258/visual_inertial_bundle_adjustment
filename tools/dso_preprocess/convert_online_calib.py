import json
import yaml
import numpy as np
from scipy.spatial.transform import Rotation as Rot

parent_path = "/home/hapq/Desktop/viba_stuff/"
calib_file = (
    parent_path + "viba_input/dso_output/intrinsics.txt"
)  # From configuration directory
stereo_file = (
    parent_path + "viba_input/dso_output/stereo.txt"
)  # From configuration directory
imu_file = (
    parent_path + "viba_input/dso_output/imu.yaml"
)  # From configuration directory
bias_file = parent_path + "viba_input/dso_output/viba_bias.txt"  # From result directory
output_file = parent_path + "viba_input/online_calibration.jsonl"


def compute_lr_transform_from_file(stereo_file):
    with open(stereo_file, "r") as f:
        tx, ty, tz, qw, qx, qy, qz = map(float, f.readline().split())

    R_lr = Rot.from_quat([qx, qy, qz, qw]).inv()
    t_lr = -R_lr.apply([tx, ty, tz])
    qx, qy, qz, qw = R_lr.as_quat()
    return np.array(t_lr), np.array([qw, qx, qy, qz])


def load_imu_transform(imu_file):
    with open(imu_file) as f:
        T = np.array(yaml.safe_load(f)["cam0"]["T_cam_imu"])

    R = Rot.from_matrix(T[:3, :3])
    qx, qy, qz, qw = R.as_quat()
    return T[:3, 3], np.array([qw, qx, qy, qz])


def create_camera(label, fx, fy, cx, cy, w, h, t, q, serial_num):
    return {
        "Calibrated": True,
        "ConfigData": {
            "ImageHeight": h,
            "ImageWidth": w,
            "MaxSolidAngle": 3.141592653589793,
        },
        "Label": label,
        "Projection": {
            "Description": "fx, fy, cx, cy",
            "Name": "Linear",
            "Params": [fx, fy, cx, cy],
        },
        "SerialNumber": serial_num,
        "T_Device_Camera": {
            "Translation": t.tolist(),
            "UnitQuaternion": [q[0], [q[1], q[2], q[3]]],
        },
    }


def create_imu(label, gyro_bias, accel_bias, t, q):
    return {
        "Accelerometer": {
            "Bias": {"Name": "Constant", "Offset": accel_bias},
            "TimeOffsetSec_Device_Accel": 0.0,
            "Model": {
                "Name": "UpperTriagonalLinear",
                "RectificationMatrix": [
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0],
                ],
            },
        },
        "Calibrated": True,
        "Gyroscope": {
            "Bias": {"Name": "Constant", "Offset": gyro_bias},
            "TimeOffsetSec_Device_Gyro": 0.0,
            "Model": {
                "Name": "Linear",
                "RectificationMatrix": [
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0],
                ],
            },
        },
        "Label": label,
        "SerialNumber": "",
        "T_Device_Imu": {
            "Translation": t.tolist(),
            "UnitQuaternion": [q[0], [q[1], q[2], q[3]]],
        },
    }


#
bias_dict = {}
with open(bias_file, "r") as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue

        parts = line.strip().split()
        ts = int(parts[0])
        bwx, bwy, bwz = map(float, parts[1:4])
        bax, bay, baz = map(float, parts[4:7])
        bias_dict[ts] = (bwx, bwy, bwz, bax, bay, baz)

#
t_lr, q_lr = compute_lr_transform_from_file(stereo_file)
t_imu, q_imu = load_imu_transform(imu_file)

#
with open(calib_file, "r") as fin, open(output_file, "w") as fout:
    for line in fin:
        if line.startswith("#") or not line.strip():
            continue

        # Intrinsics parsing
        parts = line.strip().split()
        timestamp_ns = int(parts[0])
        fx, fy, cx, cy, w, h = map(float, parts[1:7])
        tracking_timestamp_us = timestamp_ns // 1000
        utc_timestamp_ns = -1

        # Bias parsing
        if timestamp_ns in bias_dict:
            bwx, bwy, bwz, bax, bay, baz = bias_dict[timestamp_ns]
            gyro_bias = [bwx, bwy, bwz]
            accel_bias = [bax, bay, baz]
        else:
            gyro_bias = [0.0, 0.0, 0.0]
            accel_bias = [0.0, 0.0, 0.0]

        # Add entry
        entry = {
            "utc_timestamp_ns": utc_timestamp_ns,
            "tracking_timestamp_us": tracking_timestamp_us,
            "ImuCalibrations": [
                create_imu("imu-left", gyro_bias, accel_bias, t_imu, q_imu),
                create_imu("imu-right", gyro_bias, accel_bias, t_imu, q_imu),
            ],
            "CameraCalibrations": [
                create_camera(
                    "camera-slam-left",
                    fx,
                    fy,
                    cx,
                    cy,
                    w,
                    h,
                    t=np.array([0.0, 0.0, 0.0]),
                    q=np.array([1.0, 0.0, 0.0, 0.0]),
                    serial_num="0072510f1b2104050900000614170001",
                ),
                create_camera(
                    "camera-slam-right",
                    fx,
                    fy,
                    cx,
                    cy,
                    w,
                    h,
                    t=t_lr,
                    q=q_lr,
                    serial_num="0072510f1b2107010800000c0d220001",
                ),
            ],
        }
        fout.write(json.dumps(entry) + "\n")

print("Done: online_calibration.jsonl generated.")
