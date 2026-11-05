#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行脚本 V2 - 基于JSON配置
"""

import sys
from pathlib import Path
from src.graph_generator_v2 import GraphGeneratorV2


def main():
    print("=" * 60)
    print("B站视频关系图谱生成器 V2")
    print("=" * 60)
    print()
    
    # 检查数据文件
    data_file = Path('data/graph_data_v2.json')
    if not data_file.exists():
        print("✗ 未找到图谱数据文件: data/graph_data_v2.json")
        print()
        print("请先运行以下命令之一采集数据:")
        print("  1. python crawl_v2.py  - 交互式采集")
        print("  2. python src/data_processor_v2.py  - 从CSV转换")
        print()
        sys.exit(1)
    
    # 检查配置文件
    config_file = Path('config/node_config.json')
    if not config_file.exists():
        print("✗ 未找到配置文件: config/node_config.json")
        sys.exit(1)
    
    # 生成图谱
    try:
        generator = GraphGeneratorV2()
        generator.load_config().load_data().generate_html()
        
        print()
        print("=" * 60)
        print("✓ 图谱生成完成！")
        print("=" * 60)
        print()
        print("下一步:")
        print("  打开 output/graph_v2.html 查看结果")
        print()
        
    except Exception as e:
        print(f"\n✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
