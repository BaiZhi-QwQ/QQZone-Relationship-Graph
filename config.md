以下是对配置文件的详细说明文档：

---
# QQZone关系图生成器配置手册

## 一、数据目录配置
```python

DATA_ROOT = "data"  # 根数据目录
GROUP_NUMBER_DIR = os.path.join(DATA_ROOT, "group_member")  # 群成员文件存储路径
QQZONE_DATA_DIR = os.path.join(DATA_ROOT, "qqzone_data")  # QQZone原始数据目录

# 自动计算的基础路径（兼容不同操作系统）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 派生路径（建议保持默认）
DATA_DIR = os.path.join(BASE_DIR, "data/qqzone_data")  # 最终QQZone数据路径
DATA_DIR_GROUP = os.path.join(BASE_DIR, "data", "group_member")  # 最终群成员路径

```

**使用建议**：
1. 首次运行时自动创建缺失目录
2. 群成员文件应保存为`qq_member.json`
3. QQZone数据按`QQ号.json`

---

## 二、爬虫配置参数
```python
REQUEST_INTERVAL = 2  # 请求间隔(秒)，防止被封禁
MAX_EMOTIONS_PER_USER = 20  # 每个用户最多采集的说说数量
```

**调优指南**：
| 参数 | 安全范围 | 风险说明 |
|------|----------|----------|
| REQUEST_INTERVAL | ≥2秒 | <1秒可能触发反爬机制 |
| MAX_EMOTIONS | 20-50 | 过高可能导致请求超时 |

---

## 三、可视化核心配置
### 1. 输出配置
```python
OUTPUT_HTML = "network.html"  # 全局关系图输出文件
PERSONAL_OUTPUT_HTML = "personal_network_{}.html"  # 个人关系图模板
```
- `{}`会被替换为最后一个目标QQ号
- 默认输出到项目根目录

### 2. 画布配置
```python
VISUALIZATION_CONFIG = {
    "default": {
        "height": "100vh",      # 画布高度（100%视窗高度）
        "width": "100%",        # 画布宽度 
        "bgcolor": "#222222",   # 背景色（深灰色）
        "directed": True,       # 显示有向箭头[3][4]
        "notebook": False,      # 非Jupyter环境
        "cdn_resources": "in_line"  # 内联资源（离线可用）
    }
}
```

**样式修改建议**：
```python
# 修改节点颜色示例
VISUALIZATION_CONFIG["default"]["node_color"] = "#FFA500"
# 增加边透明度
VISUALIZATION_CONFIG["default"]["edge_opacity"] = 0.7
```

---

## 四、布局配置
```python
LAYOUT_CONFIG = {
    "spring": {
        "k": 0.2,        # 节点间距系数（0.1-1.0）
        "iterations": 100,  # 布局迭代次数
        "seed": 42,      # 随机种子（固定值可复现布局）
        "scale": 1000,   # 布局范围缩放比例
        "enabled": True  # 启用spring布局[3][4]
    },
    "default": {
        "enabled": False # 禁用自动布局
    }
}
```

**布局选择策略**：
| 布局类型 | 适用场景 | 性能影响 |
|----------|----------|----------|
| spring   | 全局网络 | 较高（需预计算）|
| default  | 小型网络 | 低       |

---

## 五、物理引擎配置
### 1. 全局网络参数
```python

SET_OPTION = """
{
    "physics": {
        "enabled": false,  // 禁用物理引擎（使用预计算布局）
        "stabilization": {
            "enabled": true,  // 启用稳定化
            "iterations": 1000  // 稳定化迭代次数
        }
    },
    "interaction": {
        "hover": true,  // 悬停高亮
        "selectConnectedEdges": true  // 选中关联边
    }
}
"""
```

### 2. 个人网络专用参数
```python

SET_OPTION_PERSONAL = """
{
    "physics": {
        "forceAtlas2Based": {
            "gravitationalConstant": -50,  // 引力系数（负值=斥力）
            "centralGravity": 0.01,        // 中心引力
            "springLength": 50,            // 边自然长度
            "springConstant": 0.08         // 边弹性系数
        },
        "minVelocity": 0.75,  // 最小运动速度
        "solver": "forceAtlas2Based"  // 布局算法
    }
}
"""
```

**物理参数调优指南**：
| 参数 | 调整方向 | 效果变化 |
|------|----------|----------|
| gravitationalConstant | 增大负值 | 节点间距增大 |
| springConstant | 增大值 | 边长度更稳定 |
| minVelocity | 减小值 | 布局收敛更快 |
