FROM debian:12
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    chromium chromium-driver python3-pip python3-venv \
    ttf-wqy-microhei
ADD ./ /code
RUN python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip3 install --upgrade pip && \
    pip3 install -r /code/requirements.txt
WORKDIR /code
CMD ["/venv/bin/python3", "main.py", "gw-service", "2025-03-01T00:00:00.000Z", "2025-03-02T00:00:00.000Z"]
