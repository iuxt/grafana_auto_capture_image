docker run --platform linux/amd64 --rm \
    --env-file=./.env \
    -v ./output:/tmp/output \
    -v ./:/code \
    grafana_image_renderer:2025-05-13 /venv/bin/python3 -u main.py gw-service now-30d now