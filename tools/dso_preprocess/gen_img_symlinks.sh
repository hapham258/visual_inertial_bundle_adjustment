#!/bin/bash

BASE="/media/hapq/LDATA/dense_mapping_zedx_mini/dataset_2026-04-01_17-21-00/dso"

SRC_LEFT="$BASE/cam0"
SRC_RIGHT="$BASE/cam1"

DST_LEFT="left"
DST_RIGHT="right"

PREFIX_LEFT="1201-1-"
PREFIX_RIGHT="1201-2-"

mkdir -p "$DST_LEFT" "$DST_RIGHT"

for f in "$SRC_LEFT"/*.png; do
    filename=$(basename "$f")
    ts="${filename%.png}"

    left_name="${PREFIX_LEFT}${ts}.png"
    right_name="${PREFIX_RIGHT}${ts}.png"

    ln -sf "$SRC_LEFT/$filename" "$DST_LEFT/$left_name"
    ln -sf "$SRC_RIGHT/$filename" "$DST_RIGHT/$right_name"
done
