FROM python:3.11-slim

# 设置基本环境变量
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /workspace

# 安装基础系统依赖 + uv
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# 添加 uv 到 PATH
ENV PATH="/root/.cargo/bin:${PATH}"

# 预装 Python 依赖（使用 uv，速度提升 10-100x）
COPY config/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt \
    && python -m spacy download en_core_web_md

# 配置 Jupyter 免密访问
RUN mkdir -p /root/.jupyter
COPY config/jupyter_server_config.py /root/.jupyter/jupyter_server_config.py

# 复制启动脚本
COPY scripts/entrypoint.sh /workspace/scripts/entrypoint.sh
RUN chmod +x /workspace/scripts/entrypoint.sh

# 暴露端口：Jupyter (8888) / Reflex (8700) / Reflex backend (3000)
EXPOSE 8888 8700 3000

# 默认启动交互式 shell
CMD [ "/bin/bash" ]
