```markdown
# QQZone 社交关系图谱生成器

## 📖 项目概述
通过QQZone公开数据构建用户社交关系图谱，支持：
- 好友互动关系可视化（点赞/评论/转发）
- 个人社交网络深度分析
- 群组成员关系图谱生成

## 依赖声明
- 核心爬虫功能基于 [SmartHypercube/Qzone-API](https://github.com/SmartHypercube/Qzone-API) 实现
- 稍有修改

## 🌟 核心功能
| 功能       | 对应模块  | 
|------------|----------------------|-----------|--------|
| Cookie管理 | Cookie Management    | [QQZoneCookieManager](qqzone/qr_login.py)
| 数据爬取   | Data Crawling        | [QzoneCrawler](qqzone/qzone_qq.py)
| 网络构建   | Network Construction | [QZoneNetworkBuilder](network/core/builder.py)
| 可视化     | Visualization        | [NetworkVisualizer](network/core/visualizer.py)

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
**启动main.py**
[主程序](main.py)

## -开始-
1. **生成关系图**:
[Network](test\生成完整net.py)
```python

from network.core.builder import QZoneNetworkBuilder

# 构建完整网络
builder = QZoneNetworkBuilder()
builder.build_network()
#builder.export_for_cosmograph()#导出为cvs文件

# 可视化完整网络
NetworkVisualizer.visualize(
    builder.graph, 
    builder.user_profiles, 
    builder.interactions
)

target_uin = "123456789"  # 替换为实际QQ号
    for depth in [1, 3, 5, 8]:# 深度列表
        personal_graph = PersonalNetworkGenerator.generate(builder, target_uin, depth)
        output_file = NetworkVisualizer.visualize(
            personal_graph,
            builder.user_profiles,
            builder.interactions,
            is_personal=True,
            use_layout='default'
        )

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
