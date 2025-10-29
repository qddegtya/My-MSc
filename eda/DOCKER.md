# Docker 部署指南

本项目使用 Docker 容器化部署，支持 Jupyter Lab 和 Reflex Dashboard 的独立或联合运行。

## 快速开始

### 1. 构建镜像

```bash
docker-compose build
```

构建特点：
- 使用 **uv** 作为包管理工具（速度提升 10-100x）
- 预装所有依赖（polars, plotly, pandas, numpy, bertopic, etc.）
- 预下载 spaCy 模型（`en_core_web_md`）

### 2. 运行模式

#### 模式 A: 仅 Jupyter Lab（用于数据分析）

```bash
docker-compose up jupyter
```

访问地址：`http://localhost:8888` （无密码）

#### 模式 B: 仅 Reflex Dashboard（用于可视化展示）

```bash
docker-compose up dashboard
```

访问地址：`http://localhost:8700`

#### 模式 C: 全部服务（Jupyter + Dashboard）

```bash
docker-compose up eda
```

访问地址：
- Jupyter Lab: `http://localhost:8888`
- Reflex Dashboard: `http://localhost:8700`

### 3. 分离运行（同时启动多个服务）

```bash
docker-compose up jupyter dashboard
```

这会启动两个独立容器：
- `ck-eda-jupyter`: 运行 Jupyter Lab
- `ck-eda-dashboard`: 运行 Reflex Dashboard

## 启动脚本

容器使用 `entrypoint.sh` 脚本管理启动模式：

```bash
# 手动调用启动脚本
docker run -it --rm -v $(pwd):/workspace charlie-kirk-eda:latest \
  /bin/bash /workspace/entrypoint.sh [jupyter|dashboard|all|bash]
```

支持的模式：
- `jupyter`: 仅启动 Jupyter Lab
- `dashboard`: 仅启动 Reflex Dashboard
- `all`: 同时启动 Jupyter 和 Dashboard（后台运行 Jupyter）
- `bash`: 进入交互式 shell

## 端口映射

| 服务 | 容器端口 | 主机端口 | 说明 |
|-----|---------|---------|------|
| Jupyter Lab | 8888 | 8888 | Web UI（无密码） |
| Reflex Frontend | 8700 | 8700 | Dashboard 前端 |
| Reflex Backend | 3000 | 3000 | API 后端 |

## 数据持久化

通过 volume 挂载实现代码和数据持久化：

```yaml
volumes:
  - ./:/workspace
```

容器内 `/workspace` 目录映射到项目根目录，所有修改会实时同步。

## 依赖管理

### 添加新依赖

1. 编辑 `config/requirements.txt`：
   ```
   new-package>=1.0.0
   ```

2. 重新构建镜像：
   ```bash
   docker-compose build --no-cache
   ```

### 使用 uv 安装（容器内）

```bash
# 进入容器
docker exec -it ck-eda-all bash

# 使用 uv 安装
uv pip install package-name
```

## 常见问题

### Q: 如何重置容器？

```bash
docker-compose down
docker-compose up --build
```

### Q: 如何查看容器日志？

```bash
docker-compose logs -f [jupyter|dashboard|eda]
```

### Q: 如何进入运行中的容器？

```bash
docker exec -it ck-eda-all bash
```

### Q: 镜像构建失败？

检查网络连接，uv 安装需要访问：
- https://astral.sh/uv/install.sh
- https://pypi.org

## 生产部署建议

1. **移除 volume 挂载**：在 docker-compose.yml 中注释掉 volumes，将代码打包进镜像
2. **环境变量配置**：通过 `.env` 文件管理敏感配置
3. **反向代理**：使用 Nginx/Caddy 提供 HTTPS 和域名访问
4. **资源限制**：添加 CPU/内存限制防止资源耗尽

```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
    reservations:
      cpus: '2'
      memory: 4G
```
