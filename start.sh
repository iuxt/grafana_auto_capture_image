docker run --rm \
    --env-file=./.env \
    -v $(pwd)/output:/tmp/output \
    likun /venv/bin/python3 -u main.py gw-service now-30d now