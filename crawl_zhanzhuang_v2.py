#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
采集"站桩"相关视频 - 增强版
使用更长延迟和重试机制，目标100+视频
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from bilibili_crawler import BilibiliCrawler


def crawl_with_retry(crawler, keyword, target_count=100):
    """
    智能采集，带重试机制
    """
    all_videos = []
    page = 1
    max_page = 10  # 最多尝试10页
    retry_delay = 30  # 遇到限制后等待30秒
    
    print(f"目标: 采集至少 {target_count} 个视频")
    print(f"策略: 逐页采集，遇到限制自动重试")
    print()
    
    while len(all_videos) < target_count and page <= max_page:
        print(f"\n{'='*70}")
        print(f"正在采集第 {page} 页 (已采集 {len(all_videos)} 个视频)...")
        print(f"{'='*70}")
        
        # 搜索当前页
        result = crawler.search_videos(
            keyword=keyword,
            page=page,
            page_size=20,
            duration=0,
            order='totalrank'
        )
        
        if not result:
            print(f"⚠️  第 {page} 页搜索失败，可能遇到限制")
            print(f"等待 {retry_delay} 秒后重试...")
            time.sleep(retry_delay)
            
            # 重试一次
            result = crawler.search_videos(
                keyword=keyword,
                page=page,
                page_size=20,
                duration=0,
                order='totalrank'
            )
            
            if not result:
                print(f"❌ 第 {page} 页重试失败，跳过")
                page += 1
                continue
        
        videos_list = result.get('result', [])
        if not videos_list:
            print(f"第 {page} 页没有更多结果")
            break
        
        print(f"✓ 找到 {len(videos_list)} 个视频")
        
        # 获取每个视频的详细信息
        page_videos = []
        for idx, item in enumerate(videos_list, 1):
            bvid = item.get('bvid')
            if not bvid:
                continue
            
            print(f"  [{idx}/{len(videos_list)}] {bvid}...", end=' ')
            
            video_info = crawler.get_video_info(bvid)
            if video_info:
                video_data = crawler.parse_video_data(video_info)
                page_videos.append(video_data)
                print(f"✓ {video_data['title'][:40]}...")
            else:
                print("✗ 失败")
            
            # 每个视频间延迟
            time.sleep(2.5)
        
        all_videos.extend(page_videos)
        print(f"\n第 {page} 页完成，本页成功采集 {len(page_videos)} 个视频")
        print(f"累计: {len(all_videos)} 个视频")
        
        # 检查是否达到目标
        if len(all_videos) >= target_count:
            print(f"\n🎉 已达到目标！共采集 {len(all_videos)} 个视频")
            break
        
        page += 1
        
        # 页面间延迟更长
        if page <= max_page:
            print(f"\n等待 5 秒后继续...")
            time.sleep(5)
    
    return all_videos


def main():
    print("=" * 70)
    print("  B站视频采集 - 站桩（增强版）")
    print("=" * 70)
    
    keyword = "站桩"
    target = 100
    
    print(f"\n关键词: {keyword}")
    print(f"目标数量: {target}+ 个视频")
    print(f"采集策略: 智能重试 + 长延迟")
    print()
    print("⚠️  注意:")
    print("  - 采集过程可能需要 10-20 分钟")
    print("  - 遇到限制会自动等待重试")
    print("  - 可随时按 Ctrl+C 中断")
    print()
    
    confirm = input("确认开始采集? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ 已取消")
        return
    
    print("\n" + "=" * 70)
    print("🚀 开始采集...")
    print("=" * 70)
    
    start_time = time.time()
    crawler = BilibiliCrawler()
    
    try:
        videos = crawl_with_retry(crawler, keyword, target)
        
        elapsed = time.time() - start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        if videos:
            print("\n" + "=" * 70)
            print(f"✅ 采集完成！")
            print("=" * 70)
            print(f"  耗时: {minutes}分{seconds}秒")
            print(f"  视频数: {len(videos)}")
            
            # 统计信息
            total_play = sum(v['play_count'] for v in videos)
            total_coin = sum(v['coin_count'] for v in videos)
            up_names = set(v['up_name'] for v in videos)
            
            print(f"\n📊 统计:")
            print(f"  UP主数: {len(up_names)}")
            print(f"  总播放: {total_play:,}")
            print(f"  总投币: {total_coin:,}")
            print(f"  平均播放: {total_play // len(videos):,}")
            
            # 播放量排行
            print(f"\n🔥 播放量TOP10:")
            sorted_videos = sorted(videos, key=lambda x: x['play_count'], reverse=True)
            for idx, v in enumerate(sorted_videos[:10], 1):
                print(f"  {idx}. {v['title'][:45]}...")
                print(f"     播放: {v['play_count']:,} | UP主: {v['up_name']}")
            
            # 保存数据
            print(f"\n💾 保存数据...")
            crawler.save_to_csv(videos, 'data/videos.csv')
            crawler.save_to_json(videos, 'data/videos_zhanzhuang.json')
            print(f"  ✓ data/videos.csv")
            print(f"  ✓ data/videos_zhanzhuang.json")
            
            # 生成图谱
            print("\n🎨 生成图谱...")
            import subprocess
            result = subprocess.run(
                [sys.executable, 'run.py'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✓ 图谱生成完成！")
                print("\n" + "=" * 70)
                print("📂 输出文件:")
                print("  - output/graph.html (交互式图谱)")
                print("  - data/videos.csv (CSV数据)")
                print("  - data/videos_zhanzhuang.json (JSON数据)")
                print("=" * 70)
                print("\n💡 在浏览器中打开 output/graph.html 查看可视化图谱")
            else:
                print("⚠️  图谱生成遇到问题")
        else:
            print("\n❌ 未采集到数据")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
        if 'videos' in locals() and videos:
            print(f"已采集 {len(videos)} 个视频")
            save = input("是否保存已采集的数据? (y/n): ").strip().lower()
            if save == 'y':
                crawler.save_to_csv(videos, 'data/videos.csv')
                print("✓ 数据已保存")


if __name__ == '__main__':
    main()
