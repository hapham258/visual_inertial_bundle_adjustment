import os

parent_path = os.getenv("PARENT_PATH")
input_file = (
    parent_path + "/viba_input/dso_output/imu_orig.txt"
)  # From raw data directory
output_file = parent_path + "/viba_input/imu_samples_imu-left.csv"
output_file_right = parent_path + "/viba_input/imu_samples_imu-right.csv"

with open(input_file, "r") as fin, open(output_file, "w") as fout:
    # Write new header
    fout.write(
        "#timestamp [ns], temperature [degC], "
        "w_RS_S_x [rad s^-1], w_RS_S_y [rad s^-1], w_RS_S_z [rad s^-1], "
        "a_RS_S_x [m s^-2], a_RS_S_y [m s^-2], a_RS_S_z [m s^-2]\n"
    )

    for line in fin:
        line = line.strip()

        # Skip comments or empty lines
        if not line or line.startswith("#"):
            continue

        parts = line.split()

        # Parse input
        timestamp = parts[0]
        wx, wy, wz = parts[1:4]
        ax, ay, az = parts[4:7]

        # Write output (temperature = nan)
        fout.write(f"{timestamp}, nan, {wx}, {wy}, {wz}, {ax}, {ay}, {az}\n")

os.symlink(output_file, output_file_right)
print("Conversion done!")
