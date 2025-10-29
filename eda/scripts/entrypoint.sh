#!/bin/bash
# EDA Project Entrypoint Script

set -e

MODE=${1:-jupyter}

case "$MODE" in
  jupyter)
    echo "🚀 Starting Jupyter Lab..."
    jupyter lab \
      --ip=0.0.0.0 \
      --port=8888 \
      --no-browser \
      --ServerApp.token='' \
      --ServerApp.password='' \
      --ServerApp.allow_remote_access=True \
      --IdentityProvider.token='' \
      --allow-root
    ;;

  dashboard)
    echo "📊 Starting Reflex Dashboard..."
    cd /workspace/src/app
    reflex run --env prod
    ;;

  all)
    echo "🔥 Starting both Jupyter Lab and Reflex Dashboard..."
    # Start Jupyter in background
    jupyter lab \
      --ip=0.0.0.0 \
      --port=8888 \
      --no-browser \
      --ServerApp.token='' \
      --ServerApp.password='' \
      --ServerApp.allow_remote_access=True \
      --IdentityProvider.token='' \
      --allow-root &

    # Wait for Jupyter to start
    sleep 3

    # Start Reflex dashboard
    cd /workspace/src/app
    reflex run --env prod
    ;;

  bash)
    echo "💻 Starting interactive shell..."
    exec /bin/bash
    ;;

  *)
    echo "❌ Unknown mode: $MODE"
    echo "Usage: $0 [jupyter|dashboard|all|bash]"
    exit 1
    ;;
esac
