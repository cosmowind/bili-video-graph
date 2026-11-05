#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键运行脚本：处理数据并生成图谱
"""

import sys
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_processor import DataProcessor
from graph_generator import GraphGenerator

def main():
    print("=" * 50)
    print("B站视频关系图谱生成器")
    print("=" * 50)
    
    # 检查数据文件
    data_file = Path('data/videos.csv')
    if not data_file.exists():
        print(f"\n错误: 找不到数据文件 {data_file}")
        print("请确保已使用RPA采集数据并保存为 data/videos.csv")
        print("\n数据格式示例:")
        print("bv_id,title,up_name,publish_date,play_count,coin_count,duration,has_subtitle")
        print("BV1234567890,视频标题,UP主名称,2024-01-01,10000,500,3600,是")
        return
    
    try:
        # 步骤1: 处理数据
        print("\n[1/2] 处理数据...")
        processor = DataProcessor('data/videos.csv')
        processor.load_data().create_nodes().create_edges().save_json()
        
        # 步骤2: 生成图谱
        print("\n[2/2] 生成图谱...")
        generator = GraphGenerator()
        generator.load_data().generate_html()
        
        print("\n" + "=" * 50)
        print("✓ 完成！请打开 output/graph.html 查看图谱")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
