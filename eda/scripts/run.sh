#!/bin/bash
# Reflex dashboard 启动脚本（使用 uv 环境管理）

set -e  # 遇到错误立即退出

echo "🚀 启动 Charlie Kirk Twitter Analytics Dashboard..."
echo ""

# 进入项目根目录
cd "$(dirname "$0")/.."
PROJECT_ROOT="$(pwd)"

# 1. 检查并安装 uv
echo "📦 检查 uv 工具..."
if ! command -v uv &> /dev/null; then
    echo "   uv 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo "   ✅ uv 安装完成"
else
    echo "   ✅ uv 已安装: $(uv --version)"
fi

# 2. 创建或激活虚拟环境
echo ""
echo "🔧 配置虚拟环境..."
if [ ! -d ".venv" ]; then
    echo "   创建新的虚拟环境..."
    uv venv .venv
    echo "   ✅ 虚拟环境创建完成"
else
    echo "   ✅ 虚拟环境已存在"
fi

# 3. 检查 parquet 数据文件
echo ""
echo "📊 检查数据文件..."
if [ ! -d "src/notebooks/parquet" ] || [ -z "$(ls -A src/notebooks/parquet 2>/dev/null)" ]; then
    echo "   ⚠️  警告: src/notebooks/parquet/ 目录为空或不存在"
    echo "   请先运行 notebooks 生成数据文件："
    echo "   jupyter lab"
    echo "   然后依次运行 src/notebooks/ 下的 00-03 笔记本"
    echo ""
else
    PARQUET_COUNT=$(ls src/notebooks/parquet/*.parquet 2>/dev/null | wc -l)
    echo "   ✅ 找到 ${PARQUET_COUNT} 个 parquet 文件"
fi

# 4. 安装依赖
echo ""
echo "📦 安装依赖..."
if [ -f "config/requirements.txt" ]; then
    uv pip install -r config/requirements.txt
else
    # 安装核心依赖
    uv pip install reflex polars pandas numpy plotly kaleido pyarrow
fi
echo "   ✅ 依赖安装完成"

# 5. 进入应用目录
echo ""
echo "📂 进入应用目录..."
cd src/app
echo "   ✅ 工作目录: $(pwd)"

# 6. 初始化 Reflex（如果需要）
echo ""
echo "🔧 检查 Reflex 配置..."
if [ ! -f "rxconfig.py" ]; then
    echo "   ⚠️  错误: rxconfig.py 不存在"
    exit 1
fi
echo "   ✅ Reflex 配置文件存在"

# 7. 启动应用
echo ""
echo "========================================"
echo "📊 启动 Dashboard..."
echo "========================================"
echo ""
echo "   访问地址: http://localhost:8700"
echo ""
echo "   按 Ctrl+C 停止服务"
echo ""
echo "========================================"
echo ""

# 使用 reflex 启动（已在 src/app 目录）
source "${PROJECT_ROOT}/.venv/bin/activate"
reflex run
