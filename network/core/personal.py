# 个人关系图功能
import networkx as nx
from collections import deque

class PersonalNetworkGenerator:
    @staticmethod
    def generate(builder, target_uin, depth=1):
        """
        生成个人关系子图
        :param builder: QZoneNetworkBuilder实例
        :param target_uin: 目标用户ID
        :param depth: 关系深度
        :return: 子图
        """
        if target_uin not in builder.graph:
            raise ValueError(f"用户 {target_uin} 不在网络中")
        
        subgraph = nx.DiGraph()
        queue = deque([(target_uin, 0)])
        visited = {target_uin}
        
        while queue:
            current_uin, current_depth = queue.popleft()
            
            if current_depth >= depth:
                continue
                
            neighbors = set(builder.graph.predecessors(current_uin)) | set(builder.graph.successors(current_uin))
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    subgraph.add_node(neighbor, **builder.graph.nodes[neighbor])
                    
                    # 添加双向边
                    for u, v in [(current_uin, neighbor), (neighbor, current_uin)]:
                        if builder.graph.has_edge(u, v):
                            subgraph.add_edge(u, v, **builder.graph[u][v])
                    
                    queue.append((neighbor, current_depth + 1))
        
        return subgraph