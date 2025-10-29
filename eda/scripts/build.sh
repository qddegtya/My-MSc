#!/bin/bash
# Docker Build & Test Script

set -e

echo "🏗️  Building Docker image..."
docker-compose build --no-cache

echo ""
echo "✅ Build complete!"
echo ""
echo "📋 Available commands:"
echo ""
echo "  # Run Jupyter Lab only"
echo "  docker-compose up jupyter"
echo ""
echo "  # Run Dashboard only"
echo "  docker-compose up dashboard"
echo ""
echo "  # Run both (all-in-one)"
echo "  docker-compose up eda"
echo ""
echo "  # Run in detached mode"
echo "  docker-compose up -d eda"
echo ""
echo "  # Stop all services"
echo "  docker-compose down"
echo ""

# Optional: Test if image works
read -p "🧪 Test the image now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Testing image..."
    docker run --rm charlie-kirk-eda:latest python -c "
import polars as pl
import plotly.express as px
import pandas as pd
import numpy as np
print('✅ All core dependencies working!')
"
    echo "✅ Image test passed!"
fi
