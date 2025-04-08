from network.core.builder import QZoneNetworkBuilder
from network.core.visualizer import NetworkVisualizer
from network.core.personal import PersonalNetworkGenerator
from qqzone.qr_login import QQZoneCookieManager
from qqzone.qzone_qq import QzoneCrawler
from qqzone.member_manager import MemberManager
import json

def get_depths(depths_input):
    """将输入的深度字符串转换为整数列表"""
    try:
        # 将输入的字符串分割成列表，并转换为整数
        depths = [int(d) for d in depths_input.split(',')]
        return depths
    except ValueError:
        print("输入的深度列表包含非整数值，请重新输入。")
        return None

def main():
    # 初始化网络构建器和成员管理器
    builder = QZoneNetworkBuilder()
    dm = MemberManager()
    
    while True:
        print("\n===== QQ空间社交网络分析系统 =====")
        print("1. Cookie管理")
        print("2. 构建社交网络")
        print("3. 可视化网络")
        print("4. 生成个人关系图")
        print("5. 从群成员文件加载QQ号")
        print("6. 批量爬取数据")
        print("7. 退出")
        
        choice = input("请选择操作 (1-7): ").strip()
        
        if choice == "1":
            # Cookie管理功能
            while True:
                print("\n===== QQ空间Cookie管理器 =====")
                print("1. 扫码登录添加新Cookie")
                print("2. 查看所有Cookie")
                print("3. 使用指定Cookie")
                print("4. 删除Cookie")
                print("5. 手动添加cookie")
                print("6. 返回主菜单")
                
                sub_choice = input("请选择操作 (1-6): ").strip()
                
                if sub_choice == "1":
                    name = input("输入账号备注名称 (可选): ").strip()
                    manager.get_cookie_by_qrcode(name)
                
                elif sub_choice == "2":
                    manager.list_cookies()
                    if manager.cookies:
                        idx = input("输入编号查看详情 (直接回车返回): ").strip()
                        if idx.isdigit():
                            cookie = manager.get_cookie(int(idx))
                            print(json.dumps(cookie, indent=4, ensure_ascii=False))
                
                elif sub_choice == "3":
                    manager.list_cookies()
                    if manager.cookies:
                        idx = input("选择要使用的Cookie编号: ").strip()
                        if idx.isdigit():
                            cookie = manager.get_cookie(int(idx))
                            print(f"\n已选择: {cookie['account']}")
                            print("示例使用方式:")
                            print(f"uin = '{cookie['uin']}'")
                            print(f"skey = '{cookie['skey']}'")
                
                elif sub_choice == "4":
                    manager.list_cookies()
                    if manager.cookies:
                        idx = input("选择要删除的Cookie编号: ").strip()
                        if idx.isdigit():
                            manager.delete_cookie(int(idx))
                
                elif sub_choice == "5":
                    manual_cookie = input("输入手动获取的cookie ").strip()
                    manager.add_cookie(manual_cookie)
                
                elif sub_choice == "6":
                    break
                
                else:
                    print("无效输入，请重新选择")
        
        elif choice == "2":
            # 构建完整网络
            builder.build_network()
            print("社交网络构建完成！")
        
        elif choice == "3":
            # 可视化完整网络
            NetworkVisualizer.visualize(
                builder.graph, 
                builder.user_profiles, 
                builder.interactions
            )
            print("网络可视化完成！")
        
        elif choice == "4":
            # 生成个人关系图
            target_uin = input("请输入目标QQ号: ").strip()
            depths_input = input("请选择深度列表 [1,2,3,5....]: ").strip()
            depths = get_depths(depths_input)
            if depths is None:
                print("未能正确解析深度列表，请重新运行程序。")
                return
            for depth in depths:
                personal_graph = PersonalNetworkGenerator.generate(builder, target_uin, depth)
                output_file = NetworkVisualizer.visualize(
                    personal_graph,
                    builder.user_profiles,
                    builder.interactions,
                    is_personal=True,
                    use_layout='default'
                )
                print(f"深度 {depth} 的个人关系图已保存到: {output_file}")
        
        elif choice == "5":
            # 从群成员文件加载QQ号
            group_file = input("请输入群成员文件路径 (默认: data/group_member/qq_member.json): ").strip()
            group_file = group_file if group_file else "data/group_member/qq_member.json"
            
            try:
                with open(group_file, 'r', encoding='utf-8') as f:
                    members = json.load(f)
                
                qq_numbers = [m["user_id"] for m in members["data"]]
                for qq_number in qq_numbers:
                    if dm.add_target(qq_number):
                        print(f"{qq_number} 添加访问列表成功")
                    else:
                        print(f"{qq_number} 已经添加过了")
                print(f"共加载了 {len(qq_numbers)} 个QQ号")
            except Exception as e:
                print(f"加载群成员文件失败: {e}")
        
        elif choice == "6":
            # 批量爬取数据
            if not manager.cookies:
                print("请先添加有效的Cookie！")
                continue
            
            print("开始检验cookie是否可用...ovo")
            cookie = manager.get_cookie(1)
            crawler = QzoneCrawler(cookie)
            
            # 检查cookie是否有效
            if not crawler.check_cookie_valid(cookie['uin'][1:]):
                manager.delete_cookie(1)
                print("Cookie已失效，请重新添加")
                continue
            
            print(f"使用账号: {cookie['account']} ({cookie['uin'][1:]}) 进行爬取...")
            target_number = dm.list_target()
            limit = input(f"共有 {len(target_number)} 个目标，请输入爬取数量 (默认10): ").strip()
            limit = int(limit) if limit.isdigit() else 10
            crawler.batch_crawl(target_number[:limit])
        
        elif choice == "7":
            print("退出程序")
            break
        
        else:
            print("无效输入，请重新选择")

if __name__ == "__main__":
    # 初始化管理器
    manager = QQZoneCookieManager()
    dm = MemberManager()
    main()