FROM debian:12
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    chromium chromium-driver python3-pip python3-venv \
    ttf-wqy-microhei
ADD code /code
CMD ["python3", "main.py"]