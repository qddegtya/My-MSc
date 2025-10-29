"""
Notebook 初始化脚本

在每个 notebook 开头导入此模块，自动配置 Python 路径：

```python
import init  # 自动配置路径
from src import io, analysis, profiling
```
"""

import sys
from pathlib import Path

# 获取项目根目录：src/notebooks/init.py -> src/notebooks/ -> src/ -> eda/
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 添加到 sys.path 以便导入 src 包
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print(f"✅ 项目路径已配置: {PROJECT_ROOT}")
