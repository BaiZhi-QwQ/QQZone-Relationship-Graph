# 成员配置
from .settings import DATA_DIR, DATA_DIR_GROUP
from network.utils.file_loader import extract_ids_and_nicknames

# 群成员列表
GROUP_MEMBERS = extract_ids_and_nicknames(DATA_DIR)
SPECIAL_MEMBERS = extract_ids_and_nicknames(DATA_DIR_GROUP)