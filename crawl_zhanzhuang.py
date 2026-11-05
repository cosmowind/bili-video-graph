#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
采集"站桩"相关视频
目标：至少100个视频
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from bilibili_crawler import BilibiliCrawler


def main():
    print("=" * 70)
    print("  B站视频采集 - 站桩")
    print("=" * 70)
    
    keyword = "站桩"
    
    # 配置采集参数
    print(f"\n关键词: {keyword}")
    print("目标: 至少100个视频")
    print("策略: 采集多页，每页20个视频")
    print()
    
    # 计算需要采集的页数（每页最多20个，采集6页约120个视频）
    pages_needed = 6
    
    print(f"将采集 {pages_needed} 页（预计 {pages_needed * 20} 个视频）")
    print("请求间隔: 2秒（避免被限流）")
    print()
    
    confirm = input("确认开始采集? (y/n，默认y): ").strip().lower()
    if confirm and confirm != 'y':
        print("❌ 已取消")
        return
    
    print("\n" + "=" * 70)
    print("🚀 开始采集...")
    print("=" * 70)
    print()
    
    crawler = BilibiliCrawler()
    
    # 采集视频
    videos = crawler.crawl_by_keyword(
        keyword=keyword,
        max_pages=pages_needed,
        duration=0,        # 全部时长
        order='totalrank', # 综合排序
        delay=2.0          # 2秒间隔
    )
    
    if videos:
        print("\n" + "=" * 70)
        print(f"✅ 采集完成！共获取 {len(videos)} 个视频")
        print("=" * 70)
        
        # 统计信息
        total_play = sum(v['play_count'] for v in videos)
        total_coin = sum(v['coin_count'] for v in videos)
        up_names = set(v['up_name'] for v in videos)
        
        print(f"\n📊 统计信息:")
        print(f"  视频数量: {len(videos)}")
        print(f"  UP主数量: {len(up_names)}")
        print(f"  总播放量: {total_play:,}")
        print(f"  总投币数: {total_coin:,}")
        print(f"  平均播放: {total_play // len(videos):,}")
        
        # 显示前10个视频
        print(f"\n📹 前10个视频:")
        for idx, v in enumerate(videos[:10], 1):
            print(f"  {idx}. {v['title'][:50]}...")
            print(f"     UP主: {v['up_name']} | 播放: {v['play_count']:,} | 投币: {v['coin_count']}")
        
        if len(videos) > 10:
            print(f"  ... 还有 {len(videos) - 10} 个视频")
        
        # 保存数据
        print(f"\n💾 保存数据...")
        crawler.save_to_csv(videos, 'data/videos.csv')
        crawler.save_to_json(videos, 'data/videos_zhanzhuang.json')
        
        print(f"  ✓ CSV: data/videos.csv")
        print(f"  ✓ JSON: data/videos_zhanzhuang.json")
        
        # 询问是否生成图谱
        print("\n" + "=" * 70)
        choice = input("是否立即生成图谱? (y/n，默认y): ").strip().lower()
        if not choice or choice == 'y':
            print("\n🎨 生成图谱中...")
            import subprocess
            result = subprocess.run(
                [sys.executable, 'run.py'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("\n✅ 图谱生成完成！")
                print("=" * 70)
                print("📂 输出文件:")
                print("  - output/graph.html (可视化图谱)")
                print("  - data/videos.csv (原始数据)")
                print("  - data/videos_zhanzhuang.json (JSON格式)")
                print("=" * 70)
                print("\n💡 提示: 在浏览器中打开 output/graph.html 查看交互式图谱")
            else:
                print("\n⚠️  图谱生成遇到问题")
                print(result.stdout)
                if result.stderr:
                    print(result.stderr)
        else:
            print("\n💡 稍后可运行 'python run.py' 生成图谱")
    
    else:
        print("\n" + "=" * 70)
        print("❌ 未采集到任何数据")
        print("=" * 70)
        print("\n可能的原因:")
        print("  1. 网络连接问题")
        print("  2. 遇到反爬虫限制（请稍后重试）")
        print("  3. 关键词搜索无结果")
        print("\n建议:")
        print("  - 检查网络连接")
        print("  - 等待几分钟后重试")
        print("  - 尝试其他关键词")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断采集")
        print("已采集的数据可能不完整")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
