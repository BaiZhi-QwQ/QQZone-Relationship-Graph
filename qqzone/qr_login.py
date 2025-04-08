import os,re
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

class QQZoneCookieManager:
    def __init__(self, cookie_file="qzone_cookies.json"):
        self.cookie_file = cookie_file
        self.cookies = self._load_cookies()
    
    def _load_cookies(self):
        """加载Cookie文件"""
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _save_cookies(self):
        """保存Cookie到文件"""
        with open(self.cookie_file, "w", encoding="utf-8") as f:
            json.dump(self.cookies, f, ensure_ascii=False, indent=4)
    
    def add_cookie(self,data):
        matches = re.findall(r"(\w+)=([^;]+)", data)

        # 将提取的键值对转换为字典
        cookie = {key: value for key, value in matches}
        
        if not all(key in cookie for key in ["uin", "skey"]):
            print("Cookie数据必须包含uin和skey字段!")
            time.sleep(2)
            return 
        
        new_cookie = {
            "account": cookie["uin"][1:],
            "uin": cookie["uin"],
            "skey": cookie["skey"],
            "pt4_token": cookie["pt4_token"],
            "p_skey": cookie["p_skey"],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.cookies.append(new_cookie)
        self._save_cookies()
        print(f"已添加Cookie: {new_cookie['account']}")
        return new_cookie
    
    def get_cookie_by_qrcode(self, account_name=""):
        """通过扫码登录获取新Cookie"""
        driver = webdriver.Edge()
        try:
            driver.get("https://qzone.qq.com")
            print("已打开QQ空间，请稍候...\n请等到初始化完成后登录")
            
            # 切换到登录iframe
            driver.switch_to.frame(driver.find_element(By.ID, "login_frame"))
            
            # 保存二维码
            driver.find_element(By.ID, "qrlogin_img").screenshot("qrcode.png")
            print("初始化完成\n二维码已保存到 qrcode.png，请用手机QQ扫码...或快捷登录")
            
            # 等待登录成功
            while "user.qzone.qq.com" not in driver.current_url:
                time.sleep(1)
            print("登录成功！")
            
            # 提取关键Cookie
            all_cookies = driver.get_cookies()
            new_cookie = {
                "account": account_name or f"账号{len(self.cookies)+1}",
                "uin": "",
                "skey": "",
                "p_skey": "",
                "pt4_token": "",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            for cookie in all_cookies:
                if cookie['name'] in new_cookie:
                    new_cookie[cookie['name']] = cookie['value']
            
            # 添加到列表并保存
            self.cookies.append(new_cookie)
            self._save_cookies()
            print(f"\n已添加新Cookie: {new_cookie['account']}")
            return new_cookie
            
        finally:
            driver.quit()
    
    def list_cookies(self):
        """列出所有Cookie"""
        if not self.cookies:
            print("当前没有保存任何Cookie")
            return
        
        print("\n当前保存的Cookie列表:")
        for i, cookie in enumerate(self.cookies, 1):
            print(f"{i}. {cookie['account']} (uin: {cookie['uin']})")
            
    def list_cookies_json(self):
        """返回所有uin列表"""
        return [cookie["uin"] for cookie in self.cookies]
    
    def delete_cookie(self, index):
        """删除指定Cookie"""
        if 1 <= index <= len(self.cookies):
            deleted = self.cookies.pop(index-1)
            self._save_cookies()
            print(f"已删除: {deleted['account']}")
        else:
            print("无效的索引")
    
    def get_cookie(self, index):
        """获取指定Cookie"""
        if 1 <= index <= len(self.cookies):
            return self.cookies[index-1]
        print("无效的索引")
        return None
    
    def get_cookie_json(self, uin):
        """通过uin获取Cookie（自动过滤无关字段）"""
        for cookie in self.cookies:
            if cookie.get("uin") == uin:
                # 仅返回必要字段
                return {
                    "uin": cookie["uin"],
                    "skey": cookie["skey"],
                    "p_skey": cookie["p_skey"],
                    "pt4_token": cookie["pt4_token"]
                }
        return None
    
def main(manager):
    while True:
        print("\n===== QQ空间Cookie管理器 =====")
        print("1. 扫码登录添加新Cookie")
        print("2. 查看所有Cookie")
        print("3. 使用指定Cookie")
        print("4. 删除Cookie")
        print("5. 添加cookie")
        print("6. 退出")
        
        choice = input("请选择操作 (1-6): ").strip()
        
        if choice == "1":
            name = input("输入账号备注名称 (可选): ").strip()
            manager.get_cookie_by_qrcode(name)
        
        elif choice == "2":
            manager.list_cookies()
            if manager.cookies:
                idx = input("输入编号查看详情 (直接回车返回): ").strip()
                if idx.isdigit():
                    cookie = manager.get_cookie(int(idx))
                    print(json.dumps(cookie, indent=4, ensure_ascii=False))
        
        elif choice == "3":
            manager.list_cookies()
            if manager.cookies:
                idx = input("选择要使用的Cookie编号: ").strip()
                if idx.isdigit():
                    cookie = manager.get_cookie(int(idx))
                    # 这里可以添加使用Cookie的逻辑
                    print(f"\n已选择: {cookie['account']}")
                    print("示例使用方式:")
                    print(f"uin = '{cookie['uin']}'")
                    print(f"skey = '{cookie['skey']}'")
        
        elif choice == "4":
            manager.list_cookies()
            if manager.cookies:
                idx = input("选择要删除的Cookie编号: ").strip()
                if idx.isdigit():
                    manager.delete_cookie(int(idx))
        
        elif choice == "5":
            manual_cookie = input("输入手动获取的cookie ").strip()
            manager.add_cookie(manual_cookie)
                    
        elif choice == "6":
            print("退出程序")
            break
        
        else:
            print("无效输入，请重新选择")
# 使用示例
if __name__ == "__main__":
    manager = QQZoneCookieManager()
    main(manager)