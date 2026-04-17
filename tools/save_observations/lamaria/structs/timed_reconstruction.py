from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pycolmap


@dataclass
class TimedReconstruction:
    reconstruction: pycolmap.Reconstruction = field(
        default_factory=pycolmap.Reconstruction
    )
    timestamps: dict[int, int] = field(default_factory=dict)

    @classmethod
    def read(cls, input_folder: Path) -> "TimedReconstruction":
        """Load reconstruction and timestamps from disk."""
        assert input_folder.exists(), (
            f"Input folder {input_folder} does not exist"
        )

        reconstruction = pycolmap.Reconstruction(input_folder)

        ts_path = input_folder / "timestamps.txt"
        assert ts_path.exists(), f"Timestamps file {ts_path} does not exist"
        timestamps: dict[int, int] = {}
        with open(ts_path) as f:
            for line in f:
                if line.startswith("#"):
                    continue
                frame_id, ts = line.strip().split()
                timestamps[int(frame_id)] = int(ts)

        return cls(reconstruction=reconstruction, timestamps=timestamps)

    def write(self, output_folder: Path) -> None:
        """Write reconstruction and timestamps to disk."""
        output_folder.mkdir(parents=True, exist_ok=True)
        self.reconstruction.write(output_folder.as_posix())

        ts_path = output_folder / "timestamps.txt"
        frame_ids = sorted(self.timestamps.keys())

        # sanity check
        recon_frame_ids = np.array(sorted(self.reconstruction.frames.keys()))
        assert np.array_equal(np.array(frame_ids), recon_frame_ids), (
            "Frame IDs in reconstruction and timestamps do not match"
        )

        with open(ts_path, "w") as f:
            f.write("# FrameID Timestamp(ns)\n")
            for frame_id in frame_ids:
                f.write(f"{frame_id} {self.timestamps[frame_id]}\n")

    def get_image_size(self) -> tuple[int, int]:
        cams = self.reconstruction.cameras

        # keep only valid image cameras
        valid_cams = [
            c for c in cams.values()
            if c.width > 0 and c.height > 0
        ]

        if len(valid_cams) == 0:
            raise ValueError("No valid image cameras found")

        cam = valid_cams[0]

        # sanity check
        for c in valid_cams:
            if c.width != cam.width or c.height != cam.height:
                raise ValueError("Cameras have inconsistent image sizes")

        return cam.width, cam.height
