#!/bin/bash

docker run --rm \
    -v $(pwd)/:/code \
    registry.cn-hangzhou.aliyuncs.com/iuxt/grafana_auto_capture_image:20260128 /venv/bin/python3 -u main_auto.py gac-a02-service now/M now
