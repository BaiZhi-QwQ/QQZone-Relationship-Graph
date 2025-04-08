import json
import os
from typing import List, Optional

class MemberManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.visited_file = os.path.join(data_dir, "visited_users.json")
        self.target_file = os.path.join(data_dir, "target_users.json")
        self._ensure_files()

    def _ensure_files(self):
        """确保文件存在"""
        os.makedirs(self.data_dir, exist_ok=True)
        for file in [self.visited_file, self.target_file]:
            if not os.path.exists(file):
                with open(file, "w") as f:
                    json.dump([], f)

    def list_visited(self) -> List[int]:
        """已访问用户列表"""
        with open(self.visited_file, "r") as f:
            return json.load(f)

    def list_target(self) -> List[int]:
        """待访问用户列表"""
        with open(self.target_file, "r") as f:
            return json.load(f)

    def add_target(self, uin: int) -> bool:
        """添加用户到待访问列表"""
        targets = self.list_target()
        if uin not in targets:
            targets.append(uin)
            with open(self.target_file, "w") as f:
                json.dump(targets, f)
            return True
        return False

    def move_to_visited(self, uin: int) -> bool:
        """从待访问列表移动到已访问列表"""
        targets = self.list_target()
        if uin in targets:
            targets.remove(uin)
            with open(self.target_file, "w") as f:
                json.dump(targets, f)
            self._add_visited(uin)
            return True
        return False

    def _add_visited(self, uin: int):
        """内部方法：添加到已访问列表"""
        visited = self.list_visited()
        if uin not in visited:
            visited.append(uin)
            with open(self.visited_file, "w") as f:
                json.dump(visited, f)

    def delete_visited(self, index: int, back_to_target: bool = False) -> Optional[int]:
        """删除已访问用户（可选是否移回待访问列表）"""
        visited = self.list_visited()
        if 1 <= index <= len(visited):
            uin = visited.pop(index - 1)
            with open(self.visited_file, "w") as f:
                json.dump(visited, f)
            if back_to_target:
                self.add_target(uin)
            return uin
        return None