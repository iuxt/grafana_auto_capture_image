#!/bin/bash

docker run --rm \
    -v $(pwd)/:/code \
    -e DATE_FROM="2026-01-02T00:00:00.000Z" \
    -e DATE_TO="2026-01-03T00:00:00.000Z" \
    -e UID="chery-cce-service" \
    registry.cn-hangzhou.aliyuncs.com/iuxt/grafana_auto_capture_image:20260128 /venv/bin/python3 -u main_auto.py