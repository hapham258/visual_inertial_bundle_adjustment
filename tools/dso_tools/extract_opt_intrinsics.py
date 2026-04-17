import json

parent_path = "/home/hapq/Desktop/viba_stuff/"
file1 = parent_path + "viba_output/online_calibration.jsonl"
file2 = parent_path + "viba_input/dso_output/intrinsics.txt"
output = parent_path + "viba_output/intrinsics.txt"

# --- load timestamps from file2 ---
timestamps = set()
with open(file2, "r") as f2:
    for line in f2:
        if line.startswith("#") or not line.strip():
            continue
        ts = int(line.strip().split()[0])
        timestamps.add(ts)

# --- process file1 and write matched intrinsics ---
with open(file1, "r") as f1, open(output, "w") as fout:

    # header (same as file2)
    fout.write("#timestamp[ns] fx[] fy[] cx[] cy[] w[] h[]\n")

    for line in f1:
        if not line.strip():
            continue
        data = json.loads(line)
        ts_ns = int(data["tracking_timestamp_us"]) * 1000
        if ts_ns not in timestamps:
            continue

        # find slam-left camera
        cam = None
        for c in data["CameraCalibrations"]:
            if c["Label"] == "camera-slam-left":
                cam = c
                break
        if cam is None:
            continue

        # get the intrinsics
        fx, fy, cx, cy = cam["Projection"]["Params"]
        w = cam["ConfigData"]["ImageWidth"]
        h = cam["ConfigData"]["ImageHeight"]

        # write in required format
        fout.write(f"{ts_ns} {fx:.10f} {fy:.10f} {cx:.10f} {cy:.10f} {w} {h}\n")

print("Done.")
