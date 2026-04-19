#!/usr/bin/env python3
import json
import os
import fcntl
import shutil
import hashlib
from datetime import datetime

"""
安全JSON文件读写工具类

✅ 解决所有当前致命问题：
1. 全局文件锁 - 永远不会多个进程同时写入
2. 原子写入 - 要么完全成功，要么完全不变，不会损坏半文件
3. 自动备份 - 每次写入前自动保存上一个版本
4. 写入前后校验 - 损坏的文件绝对不会替换原文件
5. 幂等操作 - 运行多少次结果都一样

所有脚本必须通过这个类来读写websites.json，禁止直接使用json.load/json.dump
"""

class SafeJsonIO:
    def __init__(self, file_path, backup_count=10):
        self.file_path = os.path.abspath(file_path)
        self.backup_dir = os.path.join(os.path.dirname(self.file_path), '.backup')
        self.backup_count = backup_count
        self.lock_file = self.file_path + '.lock'
        self.lock_fd = None

        os.makedirs(self.backup_dir, exist_ok=True)

    def __enter__(self):
        self.lock_fd = open(self.lock_file, 'w')
        try:
            fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError(f"文件 {self.file_path} 正在被其他进程修改，本次操作取消")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
        self.lock_fd.close()
        try:
            os.unlink(self.lock_file)
        except:
            pass

    def read(self):
        """安全读取文件"""
        if not os.path.exists(self.file_path):
            return None

        with open(self.file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def write(self, data):
        """安全写入文件，只有100%成功才会替换原文件"""

        # 1. 先写入临时文件
        temp_file = f"{self.file_path}.tmp.{os.getpid()}"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        # 2. 验证临时文件是否完好
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                json.load(f)
        except:
            os.unlink(temp_file)
            raise RuntimeError("写入的临时文件损坏，取消操作")

        # 3. 备份当前文件
        if os.path.exists(self.file_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.backup_dir, f"{os.path.basename(self.file_path)}.{timestamp}")
            shutil.copy2(self.file_path, backup_file)
            self._clean_old_backups()

        # 4. 原子替换 - 这一步在操作系统层面是原子的
        os.replace(temp_file, self.file_path)

        return True

    def _clean_old_backups(self):
        """只保留最近N个备份"""
        files = []
        for fn in os.listdir(self.backup_dir):
            if fn.startswith(os.path.basename(self.file_path)):
                full_path = os.path.join(self.backup_dir, fn)
                files.append((os.path.getmtime(full_path), full_path))

        files.sort(reverse=True)
        for _, path in files[self.backup_count:]:
            try:
                os.unlink(path)
            except:
                pass


# 快捷工具函数
def safe_read_json(path):
    with SafeJsonIO(path) as io:
        return io.read()

def safe_write_json(path, data):
    with SafeJsonIO(path) as io:
        return io.write(data)


if __name__ == "__main__":
    print("✅ SafeJsonIO 工具类加载成功")
    print(f"备份目录: {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', '.backup')}")
