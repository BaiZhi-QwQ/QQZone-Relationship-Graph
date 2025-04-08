# 主程序入口
from network.core.builder import QZoneNetworkBuilder
from network.core.visualizer import NetworkVisualizer
from network.core.personal import PersonalNetworkGenerator

def main():
    # 构建完整网络
    builder = QZoneNetworkBuilder()
    builder.build_network()
#    builder.export_for_cosmograph()

    
    # 可视化完整网络
    NetworkVisualizer.visualize(
        builder.graph, 
        builder.user_profiles, 
        builder.interactions
    )
    
    # 生成个人关系图示例
    target_uin = "3483421977"  # 替换为实际QQ号
    for depth in [1, 3, 5, 8]:
        personal_graph = PersonalNetworkGenerator.generate(builder, target_uin, depth)
        output_file = NetworkVisualizer.visualize(
            personal_graph,
            builder.user_profiles,
            builder.interactions,
            is_personal=True,
            use_layout='default'
        )
        print(f"深度 {depth} 的个人关系图已保存到: {output_file}")

if __name__ == "__main__":
    main()