# 全局配置
import os

#qqzone_qq
DATA_ROOT = "data"
GROUP_NUMBER_DIR = os.path.join(DATA_ROOT, "group_member")
QQZONE_DATA_DIR = os.path.join(DATA_ROOT, "qqzone_data")
REQUEST_INTERVAL = 2 #访问延迟
MAX_EMOTIONS_PER_USER = 20 #访问轮数

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据目录配置
DATA_DIR = os.path.join(BASE_DIR, "data/qqzone_data")
DATA_DIR_GROUP = os.path.join(BASE_DIR, "data", "group_member")

# 输出配置
OUTPUT_HTML = "network.html"
PERSONAL_OUTPUT_HTML = "personal_network_{}.html"  # 个人网络输出模板

# 可视化配置
VISUALIZATION_CONFIG = {
    "default": {
        "height": "100vh",
        "width": "100%",
        "bgcolor": "#222222",
        "directed": True,
        "notebook": False,
        "cdn_resources" : "in_line"
    }
}

# 预先计算布局
LAYOUT_CONFIG = {
    "spring": {
        "k": 0.2,           # 节点间距系数
        "iterations": 100,   # 迭代次数
        "seed": 42,         # 随机种子
        "scale": 1000,      # 布局范围缩放
        "enabled": True     # 是否启用
    },
    "default": {
        "enabled": False    # 不使用预计算布局
    }
}

SET_OPTION = """
{

    "physics": {
        "enabled": false,
        "stabilization": {
            "enabled": true,
            "iterations": 1000 
        }
    },
        "interaction": {
        "hover": true,
        "selectConnectedEdges": true,
        "multiselect": true
    }
}
"""

SET_OPTION_PERSONAL = """
{
    "physics": {
        "forceAtlas2Based": {
        "gravitationalConstant": -50,
        "centralGravity": 0.01,
        "springLength": 50,
        "springConstant": 0.08
        },
        "minVelocity": 0.75,
        "solver": "forceAtlas2Based"
    },
        "interaction": {
        "hover": true,
        "selectConnectedEdges": true,
        "multiselect": true
    }
}
"""