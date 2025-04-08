```markdown
# QQZone 社交关系图谱生成器

## 📖 项目概述
通过QQZone公开数据构建用户社交关系图谱，支持：
- 好友互动关系可视化（点赞/评论/转发）
- 个人社交网络深度分析
- 群组成员关系图谱生成

## 🌟 核心功能
| 功能 | Feature | 对应模块 | Module |
|------|---------|----------|--------|
| Cookie管理 | Cookie Management | [QQZoneCookieManager](qqzone/qr_login.py) | [0] |
| 数据爬取 | Data Crawling | [QzoneCrawler](qqzone/qzone_qq.py) | [2] |
| 网络构建 | Network Construction | [QZoneNetworkBuilder](network/core/builder.py) | [3] |
| 可视化 | Visualization | [NetworkVisualizer](network/core/visualizer.py) | [4] |

## 🛠️ 安装指南
```bash
# 克隆仓库
git clone https://github.com/yourname/qqzone-network.git
cd qqzone-network

# 安装依赖
pip install -r requirements.txt

# 需要Chrome驱动（自动安装）
python -c "from selenium import webdriver; webdriver.Chrome()"
```

## 🚀 快速开始
1. **添加Cookie**
```python

from qqzone.qr_login import QQZoneCookieManager
manager = QQZoneCookieManager()
manager.add_cookie("your_qq_number", "cookie_data")

```

2. **生成关系图**:
```python

from network.core.builder import QZoneNetworkBuilder

builder = QZoneNetworkBuilder()
builder._load_data("data/qqzone_data/")  # QQ号文件
builder.build_network(depth=2)  # 2度关系网络
builder.visualize()  # 生成network.html

```

## 📊 数据格式 / Data Structure
QQZone原始数据示例 ([来源](qqzone/qzone_qq.py))
```json
{
  "uin": "123456",
  "emotions": [
    {
      "content": "说说内容",
      "likers": ["111", "222"], 
      "comments": [
        {"commenter": "333", "reply_to": "111"}
      ]
    }
  ]
}
```

---

## ⚙️ 配置说明
> 📌 **提示**：完整配置文档见 ([config](config.md))   
> 🐧 推荐运行环境：Python 3.8+，Chrome 100+

```
