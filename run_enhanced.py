#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行增强版图谱生成器
"""

from src.graph_generator_enhanced import EnhancedGraphGenerator

def main():
    print("=" * 50)
    print("B站视频关系图谱 - 增强版生成器")
    print("=" * 50)
    
    generator = EnhancedGraphGenerator(
        data_path='data/graph_data.json',
        csv_path='data/videos.csv'
    )
    
    generator.load_data() \
             .load_video_details() \
             .calculate_rankings() \
             .generate_html('output/graph_enhanced.html')
    
    print("\n" + "=" * 50)
    print("✅ 增强版图谱生成完成！")
    print("📁 输出文件: output/graph_enhanced.html")
    print("=" * 50)

if __name__ == '__main__':
    main()
