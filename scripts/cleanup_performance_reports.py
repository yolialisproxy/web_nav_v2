#!/usr/bin/env python3
"""
清理性能报告，保留最新的N份
"""
import os
import sys
import glob
import argparse
from datetime import datetime

def cleanup_performance_reports(reports_dir, keep=3):
    """删除旧的性能审计报告，只保留最新的keep份"""
    if not os.path.isdir(reports_dir):
        print(f"错误: 目录不存在 {reports_dir}")
        return 1
    
    # 获取所有性能审计报告文件（假设是.json文件）
    pattern = os.path.join(reports_dir, "performance_audit_*.json")
    files = glob.glob(pattern)
    
    if not files:
        print(f"在 {reports_dir} 中没有找到性能审计报告文件")
        return 0
    
    # 按修改时间排序（最新的在前）
    files_with_time = [(f, os.path.getmtime(f)) for f in files]
    files_with_time.sort(key=lambda x: x[1], reverse=True)
    
    # 保留最新的keep份，删除其余的
    files_to_delete = files_with_time[keep:]
    
    if not files_to_delete:
        print(f"没有需要删除的旧性能报告（当前保留所有{len(files_with_time)}份）")
        return 0
    
    deleted_count = 0
    for file_path, _ in files_to_delete:
        try:
            os.remove(file_path)
            print(f"删除旧性能报告: {os.path.basename(file_path)}")
            deleted_count += 1
        except Exception as e:
            print(f"删除文件 {file_path} 失败: {e}")
    
    print(f"清理完成，删除了 {deleted_count} 份旧性能报告，保留最新的 {keep} 份")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='清理性能报告，保留最新的N份')
    parser.add_argument('--dir', required=True, help='性能报告目录路径')
    parser.add_argument('--keep', type=int, default=3, help='保留最新的报告数量（默认：3）')
    
    args = parser.parse_args()
    
    sys.exit(cleanup_performance_reports(args.dir, args.keep))
