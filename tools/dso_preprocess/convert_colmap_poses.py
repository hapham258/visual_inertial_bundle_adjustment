import numpy as np
from scipy.spatial.transform import Rotation as R

parent_path = "/home/hapq/Desktop/viba_stuff/"
input_file = parent_path + "viba_input/triangulated/model_ba/images.txt"
output_file = parent_path + "viba_input/triangulated/model_ba/poses_opt.txt"

rows = []
with open(input_file, "r") as fin:
    for line in fin:
        line = line.strip()
        if line.startswith("#") or len(line) == 0:
            continue

        tokens = line.split()
        if not tokens[-1].endswith(".png"):
            continue

        qw, qx, qy, qz = map(float, tokens[1:5])
        tx, ty, tz = map(float, tokens[5:8])
        name = tokens[9]

        # skip cam 1201-2
        if name.startswith("1201-2-"):
            continue

        # extract timestamp (int for sorting)
        timestamp_ns = int(name.split("-")[-1].replace(".png", ""))
        tvec = np.array([tx, ty, tz])
        r_wc = R.from_quat([qx, qy, qz, qw])

        # world->cam → cam->world
        r_cw = r_wc.inv()
        t_cw = -r_cw.apply(tvec)
        qx_cw, qy_cw, qz_cw, qw_cw = r_cw.as_quat()
        rows.append(
            (timestamp_ns, t_cw[0], t_cw[1], t_cw[2], qw_cw, qx_cw, qy_cw, qz_cw)
        )

# sort by timestamp
rows.sort(key=lambda x: x[0])

# write
with open(output_file, "w") as fout:
    fout.write("#timestamp[ns] tx[m] ty[m] tz[m] qw[] qx[] qy[] qz[]\n")
    for r in rows:
        fout.write(
            f"{r[0]} "
            f"{r[1]:.10f} {r[2]:.10f} {r[3]:.10f} "
            f"{r[4]:.10f} {r[5]:.10f} {r[6]:.10f} {r[7]:.10f}\n"
        )
