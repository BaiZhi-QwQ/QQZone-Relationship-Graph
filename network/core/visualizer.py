# 可视化逻辑
import networkx as nx
from pyvis.network import Network
from config import settings

class NetworkVisualizer:
    @staticmethod
    def visualize(graph, user_profiles, interactions, output_file=None, 
                is_personal=False, use_layout='spring'):
        """
        可视化网络
        :param use_layout: 布局类型 ('spring'|'default')
        """
        config = settings.VISUALIZATION_CONFIG
        net = Network(**config["default"])
        
        # 预计算布局
        pos = None
        if use_layout in settings.LAYOUT_CONFIG:
            layout_config = settings.LAYOUT_CONFIG[use_layout]
            if layout_config.get('enabled', False):
                print("正在计算点线位置中...ovo")
                pos = NetworkVisualizer._calculate_layout(graph, use_layout)
        
        print("正在绘制点线中...ovo")
        # 添加节点（带布局坐标）
        for uin in graph.nodes():
            profile = user_profiles[uin]
            stats = interactions[uin]
            
            node_config = NetworkVisualizer._configure_node(uin, profile, stats)
            if pos and uin in pos:
                node_config.update({
                    'x': pos[uin][0] * 15,
                    'y': pos[uin][1] * 15,
                    'physics': False  # 固定布局位置
                })
            net.add_node(uin, **node_config)
        
        # 添加边
        for u, v, data in graph.edges(data=True):
            edge_config = NetworkVisualizer._configure_edge(data)
            net.add_edge(u, v, **edge_config)
        
        # 保存文件
        output_file = output_file or (
            settings.PERSONAL_OUTPUT_HTML.format(uin) if is_personal 
            else settings.OUTPUT_HTML
        )
        option = settings.SET_OPTION_PERSONAL if is_personal else settings.SET_OPTION
        net.set_options(option)
        
        cdn_resources = config["default"].get("cdn_resources", "remote")
        
        if cdn_resources == "in_line":
            print("正在写入资源并生成html...ovo")
            with open(output_file, 'wb') as f:
                html_content = net.generate_html()
                f.write(html_content.encode('utf-8', errors='ignore'))
        else:
            print("正在生成html...ovo")
            net.write_html(output_file)
            
        print("已产出...oWo")
        return output_file
    
    
    
    @staticmethod
    def _calculate_layout(graph, layout_type='spring'):
        """计算节点布局位置"""
        if layout_type == 'spring':
            config = settings.LAYOUT_CONFIG['spring']
            return nx.spring_layout(
                graph,
                k=config['k'],
                iterations=config['iterations'],
                seed=config['seed'],
                scale=config['scale']
            )
        return None
    
    
    @staticmethod
    def _configure_node(uin, profile, stats):
        """配置节点样式"""
        is_member = profile['is_special']
        is_member_1 = profile['is_group_member']
        nickname = profile['nickname']
        
        # 节点大小计算
        activity_score = (
            stats['publish'] * 3 +
            stats['comments'] * 2 +
            stats['replies'] * 1.5 +
            (stats['give_likes'] + stats['receive_likes']) * 0.5
        )
        size = max(activity_score * 0.2 + 10, 15)
        
        if is_member:
            color = "#FF6B6B"  # 特殊人员-柔和的珊瑚红( 特殊人员
        elif is_member_1:
            color = "#FFA500"  # 普通群成员-橙色 ( 普通成员
        else:
            color = "#4ECDC4"  # 其他用户-# 蓝色 ( 外部用户
        
        # 提示信息
        tooltip = f"""
        {nickname} ({'群成员' if is_member else 'QQ用户'})
        QQ_id：{uin}
        📝 发帖: {stats['publish']}
        💬 评论: {stats['comments']}
        ↩️ 回复: {stats['replies']}
        ❤️ 获赞: {stats['receive_likes']}
        👍 点赞: {stats['give_likes']}
        """
        
        font_config = {
        'size': 64 if is_member else 32,  # 特殊人员更大字号
        'weight': 'bold' if is_member else 'normal',
        'color': 'white' if is_member else 'rgba(248, 248, 248, 0.5)'
        }
        
        return {
            'label': nickname,
            'size': size,
            'color': color,
            'title': tooltip,
            'font': font_config,
            'physics': True
        }
    
    @staticmethod
    def _configure_edge(data):
        """配置边样式"""
        # 定义颜色映射
        color_map = {
            'like': "#5A4444",
            'comment': "#555555",
            'reply': "#3A1A62"
        }
        color_map_ = {
            'like': "#ff0000",
            'comment': "#66FF00",
            'reply': "#ff9900"
        }
        # 提取互动类型及其计数
        like_count = data.get('like_count', 0)
        comment_count = data.get('comment_count', 0)
        reply_count = data.get('reply_count', 0)
        
        # 确定主要互动类型
        max_count = max(like_count, comment_count, reply_count)
        if max_count == like_count:
            main_type = 'like'
        elif max_count == comment_count:
            main_type = 'comment'
        else:
            main_type = 'reply'
        
        # 计算主要互动类型的占比
        total_weight = data['weight']
        main_ratio = max_count / total_weight if total_weight > 0 else 0
        
        # 获取基础颜色
        base_color = color_map[main_type]
        highlight_color = color_map_[main_type]
        # 将十六进制颜色转换为 RGB
        base_rgb = tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5))
        # 根据占比调整 RGB 值
        adjusted_rgb = tuple(int(c * main_ratio) for c in base_rgb)
        # 转换回十六进制颜色值
        adjusted_color = "#{:02x}{:02x}{:02x}".format(*adjusted_rgb)
        
        # 配置边样式
        return {
            'width': data['weight'] * 0.3 + 1,  # 根据权重调整边的宽度
            'color': {
                'color': adjusted_color,
                'highlight':  highlight_color,   # 选中时颜色
                'hover': 'white',# 保持原颜色
                'opacity': 0.6#ff9900
                # 设置透明度 (0-1)
            },  # 使用调整后的颜色
            'title': f"互动类型: like={like_count}, comment={comment_count}, reply={reply_count}\n总次数: {data['weight']}",
            'arrows': 'to'  # 添加箭头
        }