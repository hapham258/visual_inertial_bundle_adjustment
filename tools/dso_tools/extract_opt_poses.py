import csv
import os

parent_path = os.getenv("PARENT_PATH")
file1 = parent_path + "/viba_output/closed_loop_framerate_trajectory.csv"
file2 = parent_path + "/viba_input/dso_output/poses.txt"
output = parent_path + "/viba_output/poses.txt"

# --- load timestamps from file2 ---
timestamps = set()
with open(file2, "r") as f2:
    for line in f2:
        if line.startswith("#") or not line.strip():
            continue
        ts = int(line.strip().split()[0])
        timestamps.add(ts)

# --- process file1 and write matched poses ---
with open(file1, "r") as f1, open(output, "w") as fout:
    reader = csv.DictReader(f1)

    # header (same as file2)
    fout.write("#timestamp[ns] tx[m] ty[m] tz[m] qw[] qx[] qy[] qz[]\n")

    for row in reader:
        ts_ns = int(row["tracking_timestamp_us"]) * 1000

        if ts_ns not in timestamps:
            continue

        # translation
        tx = float(row["tx_world_device"])
        ty = float(row["ty_world_device"])
        tz = float(row["tz_world_device"])

        # quaternion (reorder!)
        qx = float(row["qx_world_device"])
        qy = float(row["qy_world_device"])
        qz = float(row["qz_world_device"])
        qw = float(row["qw_world_device"])

        # write in required format
        fout.write(
            f"{ts_ns} {tx:.10f} {ty:.10f} {tz:.10f} {qw:.10f} {qx:.10f} {qy:.10f} {qz:.10f}\n"
        )

print("Done.")
