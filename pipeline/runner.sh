#!/bin/bash
export PATH="$(pwd):$PATH"
python3 download_s3_files.py
/bin/bash Beiwe-Analysis/Pipeline/${FREQ}.sh
