#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本：使用示例数据生成演示图谱
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_processor import DataProcessor
from graph_generator import GraphGenerator

def main():
    print("=" * 50)
    print("使用示例数据生成演示图谱")
    print("=" * 50)
    
    try:
        # 使用示例数据
        print("\n[1/2] 处理示例数据...")
        processor = DataProcessor('data/videos_sample.csv')
        processor.load_data().create_nodes().create_edges().save_json('data/demo_graph_data.json')
        
        print("\n[2/2] 生成演示图谱...")
        generator = GraphGenerator('data/demo_graph_data.json')
        generator.load_data().generate_html('output/demo_graph.html')
        
        print("\n" + "=" * 50)
        print("✓ 演示图谱已生成！")
        print("请打开 output/demo_graph.html 查看效果")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
