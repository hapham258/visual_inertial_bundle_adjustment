import os
import numpy as np
from scipy.spatial.transform import Rotation as Rot
from read_write_model import read_images_binary, read_cameras_binary

parent_path = os.getenv("PARENT_PATH")
input_path = parent_path + "/viba_input/triangulated/model_ba/"
pose_file = parent_path + "/viba_input/triangulated/model_ba/poses.txt"
intr_file = parent_path + "/viba_input/triangulated/model_ba/intrinsics.txt"

images = read_images_binary(os.path.join(input_path, "images.bin"))
cameras = read_cameras_binary(os.path.join(input_path, "cameras.bin"))
pose_rows = []
intr_rows = []
for _, img in images.items():
    name = img.name
    if name.startswith("1201-2-"):
        continue

    # Extract pose
    timestamp_ns = int(os.path.splitext(name)[0].split("-")[-1])
    qw, qx, qy, qz = img.qvec
    tx, ty, tz = img.tvec
    tvec = np.array([tx, ty, tz])
    r_wc = Rot.from_quat([qx, qy, qz, qw])
    r_cw = r_wc.inv()
    t_cw = -r_cw.apply(tvec)
    qx_cw, qy_cw, qz_cw, qw_cw = r_cw.as_quat()
    pose_rows.append(
        (timestamp_ns, t_cw[0], t_cw[1], t_cw[2], qw_cw, qx_cw, qy_cw, qz_cw)
    )

    # Extract intrinsics
    cam = cameras[img.camera_id]
    model = cam.model
    w, h = cam.width, cam.height
    params = cam.params
    if model == "PINHOLE":
        fx, fy, cx, cy = params[:4]
    else:
        raise ValueError(f"Unsupported camera model: {model}")
    intr_rows.append((timestamp_ns, fx, fy, cx, cy, w, h))

# Sort and write both consistently
pose_rows.sort(key=lambda x: x[0])
intr_rows.sort(key=lambda x: x[0])
with open(pose_file, "w") as fout:
    fout.write("#timestamp[ns] tx[m] ty[m] tz[m] qw[] qx[] qy[] qz[]\n")
    for r in pose_rows:
        fout.write(
            f"{r[0]} "
            f"{r[1]:.10f} {r[2]:.10f} {r[3]:.10f} "
            f"{r[4]:.10f} {r[5]:.10f} {r[6]:.10f} {r[7]:.10f}\n"
        )
with open(intr_file, "w") as fout:
    fout.write("#timestamp[ns] fx[] fy[] cx[] cy[] w[] h[]\n")
    for r in intr_rows:
        fout.write(
            f"{r[0]} "
            f"{r[1]:.10f} {r[2]:.10f} {r[3]:.10f} {r[4]:.10f} "
            f"{r[5]} {r[6]}\n"
        )
