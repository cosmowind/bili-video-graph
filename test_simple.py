#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试：采集几个已知的视频
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from bilibili_crawler import BilibiliCrawler


def main():
    print("=" * 60)
    print("简单测试：采集已知视频")
    print("=" * 60)
    
    # 使用已知的BV号列表
    bvids = [
        'BV1RY4y1F7pG',  # 戴锦华：历史与人民的记忆
        'BV1ux4y1e7Yi',  # 公开课
        'BV1Jq4y1Q7Ar',  # 破镜而出
    ]
    
    print(f"\n将采集 {len(bvids)} 个视频...\n")
    
    crawler = BilibiliCrawler()
    videos = crawler.crawl_by_bvids(bvids, delay=2.0)
    
    if videos:
        print(f"\n✅ 成功采集 {len(videos)} 个视频\n")
        
        # 显示采集结果
        for idx, v in enumerate(videos, 1):
            print(f"{idx}. {v['title'][:40]}...")
            print(f"   UP主: {v['up_name']}")
            print(f"   播放: {v['play_count']:,}")
            print(f"   日期: {v['publish_date']}")
            print()
        
        # 保存数据
        print("保存数据...")
        crawler.save_to_csv(videos, 'data/videos.csv')
        print("✓ 已保存到 data/videos.csv")
        
        # 询问是否生成图谱
        print("\n" + "=" * 60)
        choice = input("是否立即生成图谱? (y/n): ").strip().lower()
        if choice == 'y':
            print("\n生成图谱中...")
            import subprocess
            result = subprocess.run([sys.executable, 'run.py'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ 图谱生成完成！")
                print("请打开 output/graph.html 查看")
            else:
                print("生成过程:")
                print(result.stdout)
    else:
        print("\n❌ 采集失败")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
