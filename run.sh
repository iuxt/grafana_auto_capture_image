#!/bin/bash

docker run --rm \
    -v $(pwd)/:/code \
    -e DATE_FROM="now/M" \
    -e DATE_TO="now" \
    -e UID="chery-cce-service" \
    registry.cn-hangzhou.aliyuncs.com/iuxt/grafana_auto_capture_image:20260129 /venv/bin/python3 -u main_auto.py