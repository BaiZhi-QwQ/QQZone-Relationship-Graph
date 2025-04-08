#!/usr/bin/python3
# encoding=utf-8
import os
import json
import time
from qqzone.qzone import Qzone, NotLoaded
from qqzone.qr_login import QQZoneCookieManager,main
from qqzone.member_manager import MemberManager
from config import settings
# 常量定义
DATA_ROOT = settings.DATA_ROOT
GROUP_NUMBER_DIR = settings.GROUP_NUMBER_DIR
QQZONE_DATA_DIR = settings.QQZONE_DATA_DIR
REQUEST_INTERVAL = settings.REQUEST_INTERVAL
MAX_EMOTIONS_PER_USER = settings.MAX_EMOTIONS_PER_USER

class QzoneDataManager:
    """数据存储管理器"""
    def __init__(self):
        os.makedirs(GROUP_NUMBER_DIR, exist_ok=True)
        os.makedirs(QQZONE_DATA_DIR, exist_ok=True)
        self.user_manager = MemberManager()
    
    def save_user_emotions(self, uin, emotions):
        """保存用户说说数据（合并为一个文件）"""
        output_file = os.path.join(QQZONE_DATA_DIR, f"emotions_{uin}.json")
        data = {
            "uin": uin,
            "nickname": emotions[0].nickname,
            "timestamp": int(time.time()),
            "emotions": [self._serialize_emotion(e) for e in emotions]
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return output_file
    
    def _serialize_emotion(self, emotion):
        """序列化说说对象"""
        return {
            "tid": emotion.tid,
            "content": emotion.content if emotion.content is not NotLoaded else emotion.shortcon,
            "ctime": emotion.ctime,
            "author": emotion.author,
            "pictures": [pic.url for pic in emotion.pictures if pic is not NotLoaded],
            "videos": [pic.video_url for pic in emotion.pictures  if pic is not NotLoaded and hasattr(pic, 'video_url') and pic.video_url],#确保url不为空
            "comments": [self._serialize_comment(c) for c in emotion.comments],
            "likers": list(emotion.like.keys()) if emotion.like is not NotLoaded else []
        }
    
    def _serialize_comment(self, comment):
        """序列化评论对象"""
        self.user_manager.add_target(comment.author)
        return {
            "author": comment.author,
            "nickname": comment.nickname,
            "content": comment.content,
            "ctime": comment.ctime,
            "replys": [self._serialize_comment(r) for r in comment.replys]
        }

class QzoneCrawler:
    """爬虫主类"""
    def __init__(self, cookie):
        valid_keys = {"uin", "skey", "p_skey", "pt4_token"}
        self.filtered_cookie = {k: v for k, v in cookie.items() if k in valid_keys}
        
        self.qzone = Qzone(**self.filtered_cookie)
        self.cookie_manager = QQZoneCookieManager()
        self.data_manager = QzoneDataManager()
        self.visited_users = self.data_manager.user_manager.list_visited()
    
    def reload_qzone(self, new_cookie):
        valid_keys = {"uin", "skey", "p_skey", "pt4_token"}
        self.filtered_cookie = {k: v for k, v in new_cookie.items() if k in valid_keys}
        self.qzone = Qzone(**self.filtered_cookie)
    
    def crawl_user_emotions(self, uin, max_emotions=MAX_EMOTIONS_PER_USER):
        """爬取用户说说数据"""
        print(f"开始爬取用户 {uin} 的说说...")
        self.data_manager.user_manager.move_to_visited(uin)
        emotions = self.qzone.emotion_list(uin, num=max_emotions)
        
        if emotions is None:
            print(f"错误：无法获取用户 {uin} 的说说列表，可能权限不足或Cookie失效")
            # 将用户移回未访问列表以便后续重试
            #self.data_manager.user_manager.move_to_visited(uin)
            # 抛出异常触发上层Cookie检查与更换
            raise Exception(f"获取用户 {uin} 的说说列表失败")
        
        # 加载完整数据
        for emotion in emotions:
            if any([attr is NotLoaded for attr in [emotion.content, emotion.like, emotion.comments]]):
                emotion.load()
            print(f"正在获取{emotion.nickname}({emotion.author})的{emotion.tid}说说...")
            time.sleep(REQUEST_INTERVAL)
        
        output_file = self.data_manager.save_user_emotions(uin, emotions)
        return output_file
    
    def batch_crawl(self, qq_numbers):
        """批量爬取多个用户"""
        for uin in qq_numbers:
            try:
                if uin in self.visited_users:
                    print(f"用户 {uin} 已爬过，跳过")
                else:
                    print(f"启动延迟{REQUEST_INTERVAL}秒,防止访问高频ing...")
                    time.sleep(REQUEST_INTERVAL)
                    self.crawl_user_emotions(uin)
            except Exception as e:
                print(f"爬取用户 {uin} 失败: {str(e)}")
                if not self.check_cookie_valid(self.filtered_cookie['uin'][1:]):
                    for cookie_id in self.cookie_manager.list_cookies_json():
                        cookie = self.cookie_manager.get_cookie_json(cookie_id)
                        if not cookie:
                            continue
                        self.reload_qzone(cookie)
                        if self.check_cookie_valid(cookie['uin'][1:]):
                            print(f"使用新Cookie重试: {cookie_id}")
                            break
            
    def check_cookie_valid(self,uin):
        try:
            test_uin = uin  # 用已知可访问的测试账号
            test_data = self.qzone.emotion_list(uin=test_uin, num=1)
            if not test_data:
                raise ValueError("测试账号数据获取失败")
            print("✅ Cookie有效性验证通过")
            return True
        except Exception as e:
            print("❌ Cookie验证失败:", str(e))
            return False
    
if __name__ == "__main__":
    # 1. 初始化
    manager = QQZoneCookieManager()
    dm = MemberManager()
    main(manager)
    
    cookie_count = len(manager.cookies)
    for i in range(cookie_count):
        cookie = manager.get_cookie(1)
        crawler = QzoneCrawler(cookie)
        # 检查新创建的 crawler 的 cookie 是否有效
        if not crawler.check_cookie_valid(cookie['uin'][1:]):
            manager.delete_cookie(1)
        else:
            print(f"账号: {cookie['account']} ({cookie['uin'][1:]})可用...ovo")
            break
    
    group_file = "data\group_member\qq_member.json"
    # 3. 从群成员文件加载QQ号
    with open(group_file, 'r', encoding='utf-8') as f:
        members = json.load(f)
        
    qq_numbers = [m["user_id"] for m in members["data"]]
    for qq_number in qq_numbers:
        if dm.add_target(qq_number):
            print(f"{qq_number}添加访问列表成功")
        else:
            print(f"{qq_number}已经添加过了")
            
    target_number = dm.list_target()
    crawler.batch_crawl(target_number[:10])  # 限制前10个用户