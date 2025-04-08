# 网络构建核心类
import re
import networkx as nx
import pandas as pd
from collections import defaultdict
from config import settings
from datetime import datetime
from config.members import GROUP_MEMBERS, SPECIAL_MEMBERS
from network.utils.file_loader import load_json_data

class QZoneNetworkBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.user_profiles = {}
        self.interactions = defaultdict(lambda: {
            'publish': 0,
            'receive_likes': 0,
            'give_likes': 0,
            'comments': 0,
            'replies': 0
        })
        self.processed_users = set()
    
    def export_for_cosmograph(self, prefix="qzone"):
        """
        导出完整数据供Cosmograph使用（包括Graph模式和Embedding模式）
        :param prefix: 输出文件前缀
        """
        # 导出Graph模式所需文件
        self._export_graph_mode(prefix)
        
        # 导出Embedding模式所需文件
        self._export_embedding_mode(prefix)
        
        # 导出原始交互统计数据
        self._export_interaction_stats(f"{prefix}_interactions.csv")
        
        print(f"导出完成！文件前缀: {prefix}_*.csv")

    def _export_graph_mode(self, prefix):
        """导出Graph模式所需文件（边列表+节点元数据）"""
        # 边列表（包含所有交互类型）
        edges_data = []
        for src, tgt, attrs in self.graph.edges(data=True):
            edge = {
                "source": src,
                "target": tgt,
                "weight": attrs["weight"],
                "like_count": attrs.get("like_count", 0),
                "comment_count": attrs.get("comment_count", 0),
                "reply_count": attrs.get("reply_count", 0),
                "total_interactions": attrs["weight"],  # 兼容字段
                "first_interaction_time": datetime.now().strftime("%Y-%m-%d")  # 示例时间
            }
            edges_data.append(edge)
        
        pd.DataFrame(edges_data).to_csv(f"{prefix}_edges.csv", index=False, sep=";")
        
        # 节点元数据（包含所有属性）
        nodes_data = []
        for uin, attrs in self.user_profiles.items():
            interactions = self.interactions.get(uin, {})
            node = {
                "id": uin,
                "nickname": attrs["nickname"],
                "is_group_member": attrs["is_group_member"],
                "is_special": attrs["is_special"],
                "publish_count": interactions.get("publish", 0),
                "receive_likes": interactions.get("receive_likes", 0),
                "give_likes": interactions.get("give_likes", 0),
                "comments_made": interactions.get("comments", 0),
                "replies_made": interactions.get("replies", 0),
                "activity_score": sum(interactions.values()),  # 综合活跃度
                "node_type": "special" if attrs["is_special"] else "group" if attrs["is_group_member"] else "normal"
            }
            nodes_data.append(node)
        
        pd.DataFrame(nodes_data).to_csv(f"{prefix}_nodes.csv", index=False, sep=";")

    def _export_embedding_mode(self, prefix):
        """导出Embedding模式所需文件（带模拟坐标的节点数据）"""
        # 使用networkx的布局算法生成坐标
        pos = nx.spring_layout(self.graph, seed=42)
        
        nodes_data = []
        for uin, attrs in self.user_profiles.items():
            x, y = pos.get(uin, [0, 0])
            node = {
                "id": uin,
                "x": x,
                "y": y,
                "nickname": attrs["nickname"],
                "color": "#FF0000" if attrs["is_special"] else "#00FF00" if attrs["is_group_member"] else "#0000FF",
                "size": min(50, 5 + self.interactions.get(uin, {}).get("publish", 0) * 2),
                "activity": sum(self.interactions.get(uin, {}).values())
            }
            nodes_data.append(node)
        
        pd.DataFrame(nodes_data).to_csv(f"{prefix}_embedding.csv", index=False, sep=";")

    def _export_interaction_stats(self, path):
        """导出原始交互统计数据"""
        stats_data = []
        for uin, counts in self.interactions.items():
            stats = {"uin": uin, **counts}
            stats_data.append(stats)
        
        pd.DataFrame(stats_data).to_csv(path, index=False)

    def export_gexf(self, path="network.gexf"):
        """导出为GEXF格式（兼容Gephi）"""
        nx.write_gexf(self.graph, path)
    
    def build_network(self):
        """构建完整社交网络"""
        self._load_data()
    
    def _load_data(self,path = settings.DATA_DIR):
        """加载所有JSON数据"""
        for data in load_json_data(path):
            self._process_data(data)
    
    def _process_data(self, data):
        """处理单个用户数据（增加去重检查）"""
        if not data or 'uin' not in data:
            return
            
        owner_uin = str(data['uin'])
        
        if owner_uin in self.processed_users:
            print(f"警告：用户 {owner_uin} 的数据已处理，跳过重复文件")
            return
        self.processed_users.add(owner_uin)
        
        # 获取精确的说说列表（增强空值处理）
        emotions = data.get('emotions')
        if not isinstance(emotions, list):
            print(f"用户 {owner_uin} 的emotions字段格式异常")
            emotions = []
        
        # 统计发布量
        valid_emotions = [e for e in emotions if isinstance(e, dict)]
        post_count = len(valid_emotions)
        self.interactions[owner_uin]['publish'] = post_count  # 使用赋值而非累加
        
        print(f"用户 {owner_uin} 发帖数统计: {post_count}（原始数据长度: {len(emotions)}）")  # 调试日志
        
        # 处理每条说说
        for emotion in valid_emotions:
            self._process_emotion(owner_uin, emotion)
        
        # 处理说说数据（增加空值保护）
        for emotion in data.get('emotions', []) or []:  # 处理None值情况
            self._process_emotion(owner_uin, emotion)
        
        self._register_user(owner_uin, data.get('nickname', '未知用户'),True)#注册，修正名称
        
    def _register_user(self, uin, nickname,force = None):
        """注册用户到网络（增加去重检查）"""
        if uin not in self.user_profiles:
            self.graph.add_node(uin)
            self.user_profiles[uin] = {
                'nickname': nickname,
                'is_group_member': uin in GROUP_MEMBERS,
                'is_special': uin in SPECIAL_MEMBERS
            }
        if force:
            self.graph.add_node(uin)
            self.user_profiles[uin] = {
                'nickname': nickname,
                'is_group_member': uin in GROUP_MEMBERS,
                'is_special': uin in SPECIAL_MEMBERS
            }
    
    def _process_emotion(self, owner_uin, emotion):
        """处理单条说说（增加字段存在性检查）"""
        # 处理点赞（增加空列表保护）
        for liker_uin in map(str, emotion.get('likers', []) or []):
            self._register_user(liker_uin, f"用户{liker_uin}")
            self._add_interaction(liker_uin, owner_uin, 'like')
        
        # 处理评论（增加空列表保护）
        for comment in emotion.get('comments', []) or []:
            self._process_comment(owner_uin, comment)
    
    def _process_comment(self, owner_uin, comment):
        """处理评论及回复（增强健壮性）"""
        if not isinstance(comment, dict):
            return
            
        commenter_uin = str(comment.get('author', ''))
        nickname = str(comment.get('nickname', ''))
        self._register_user(commenter_uin, nickname, True)
        
        # 添加评论关系
        self._add_interaction(commenter_uin, owner_uin, 'comment')
        
        # 处理回复（增加空列表保护）
        for reply in comment.get('reply_to', []) or []:
            self._process_reply(reply)
    
    def _process_reply(self, reply):
        """处理回复关系（增加类型检查）"""
        if not isinstance(reply, dict):
            return
            
        replier_uin = str(reply.get('author', ''))
        target_uin = self._find_reply_target(reply)
        
        if target_uin:
            self._register_user(replier_uin, reply.get('nickname', '未知用户'))
            self._add_interaction(replier_uin, target_uin,'reply')
    
    def _find_reply_target(self, reply):
        """智能识别回复目标（增强空值处理）"""
        # 提取 reply_content 中的 @{...} 部分
        match = re.search(r'@\{([^}]*)\}', reply['reply_content'])
        if match:
            # 提取内部的键值对字符串
            inner_content = match.group(1)
            # 将键值对字符串解析为字典
            reply_info = dict(item.split(':', 1) for item in inner_content.split(','))
            # 提取 uin
            replied_uin = reply_info.get('uin')
            return replied_uin
        else:
            #"reply_content 中没有找到被回复者信息"
            return None
    
    def _add_interaction(self, source, target, itype):
        """记录互动关系（增加有效性检查）"""
        if not source or not target:
            return
            
        # 更新统计
        if itype == 'like':
            self.interactions[source]['give_likes'] += 1
            self.interactions[target]['receive_likes'] += 1
        elif itype == 'comment':
            self.interactions[source]['comments'] += 1
        elif itype == 'reply':
            self.interactions[source]['replies'] += 1
        
        # 更新关系图（增加自环检查）
        if source == target:
            return
        
        if self.graph.has_edge(source, target):
            # 增加总权重
            self.graph[source][target]['weight'] += 1
            # 根据类型更新具体计数器
            if itype == 'like':
                self.graph[source][target]['like_count'] += 1
            elif itype == 'comment':
                self.graph[source][target]['comment_count'] += 1
            elif itype == 'reply':
                self.graph[source][target]['reply_count'] += 1
        else:
            # 初始化边时设置各类型计数器
            initial_counts = {
                'weight': 1,
                'like_count': 1 if itype == 'like' else 0,
                'comment_count': 1 if itype == 'comment' else 0,
                'reply_count': 1 if itype == 'reply' else 0
            }
            self.graph.add_edge(source, target, **initial_counts)