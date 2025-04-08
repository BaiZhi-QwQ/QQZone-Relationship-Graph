import os
import json
from typing import List

def extract_ids_and_nicknames(folder_path):
    group_members = {}
    
    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    # 提取 id 和 nickname
                    _data = data.get("data")
                    if _data:
                        for user in _data:
                            user_id_group = user.get("user_id")
                            group_id = user.get("group_id")
                            nickname = user.get("nickname")
                            if group_id and nickname:
                                group_members[str(user_id_group)] = nickname
                    else:
                        user_id = data.get("uin")
                        nickname = data.get("nickname")
                        if user_id and nickname:
                            group_members[str(user_id)] = nickname
                except json.JSONDecodeError as e:
                    print(f"解析文件 {file_path} 时出错: {e}")
    
    return group_members

def load_json_data(data_dir: str) -> List[dict]:
    """加载目录中的所有JSON数据"""
    data = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                    data.append(json.load(f))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
    return data

if __name__ == "__main__":
    # 示例用法
    folder_path = "qqzone_data"  # 替换为你的文件夹路径
    folder_path = "data\group_member"
    GROUP_MEMBERS = extract_ids_and_nicknames(folder_path)

    # 现在 GROUP_MEMBERS 是一个字典，可以直接在代码中使用
    print(GROUP_MEMBERS)  # 如果需要查看内容