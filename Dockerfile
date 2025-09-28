FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/debian:12
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    chromium \
    chromium-driver \
    python3-pip \
    python3-venv \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    wget \
    xdg-utils \
    fonts-noto-cjk \
    ttf-wqy-microhei && \
    fc-cache -f -v && \
    apt clean all
ADD requirements.txt /code/requirements.txt
RUN python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip config set global.index-url https://mirrors.ustc.edu.cn/pypi/simple && \
    pip install --upgrade pip && \
    pip install -r /code/requirements.txt
WORKDIR /code
CMD ["/venv/bin/python3"]
