#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试B站API连接和采集功能
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from bilibili_crawler import BilibiliCrawler


def test_search():
    """测试搜索功能"""
    print("=" * 60)
    print("测试1: 搜索API")
    print("=" * 60)
    
    crawler = BilibiliCrawler()
    result = crawler.search_videos(keyword="戴锦华", page=1, page_size=3)
    
    if result:
        videos = result.get('result', [])
        print(f"✓ 搜索成功，找到 {len(videos)} 个结果")
        for idx, video in enumerate(videos, 1):
            print(f"  {idx}. {video.get('title', 'N/A')[:40]}...")
            print(f"     BV号: {video.get('bvid', 'N/A')}")
        return True
    else:
        print("✗ 搜索失败")
        return False


def test_video_info():
    """测试获取视频详情"""
    print("\n" + "=" * 60)
    print("测试2: 视频详情API")
    print("=" * 60)
    
    crawler = BilibiliCrawler()
    # 使用一个已知存在的视频
    bvid = "BV1RY4y1F7pG"
    
    video_info = crawler.get_video_info(bvid)
    
    if video_info:
        print(f"✓ 获取视频详情成功")
        print(f"  标题: {video_info.get('title', 'N/A')}")
        print(f"  UP主: {video_info.get('owner', {}).get('name', 'N/A')}")
        print(f"  播放: {video_info.get('stat', {}).get('view', 0):,}")
        print(f"  时长: {video_info.get('duration', 0)}秒")
        return True
    else:
        print("✗ 获取视频详情失败")
        return False


def test_crawl():
    """测试完整采集流程"""
    print("\n" + "=" * 60)
    print("测试3: 完整采集流程")
    print("=" * 60)
    
    crawler = BilibiliCrawler()
    
    print("采集2个视频...")
    videos = crawler.crawl_by_keyword(
        keyword="戴锦华",
        max_pages=1,
        duration=0,
        order='totalrank',
        delay=1.0
    )
    
    if videos:
        print(f"\n✓ 采集成功，共 {len(videos)} 个视频")
        
        # 显示第一个视频的详细信息
        if videos:
            v = videos[0]
            print(f"\n示例数据:")
            print(f"  BV号: {v['bv_id']}")
            print(f"  标题: {v['title'][:40]}...")
            print(f"  UP主: {v['up_name']}")
            print(f"  日期: {v['publish_date']}")
            print(f"  播放: {v['play_count']:,}")
            print(f"  投币: {v['coin_count']}")
            print(f"  时长: {v['duration']}秒")
            print(f"  字幕: {v['has_subtitle']}")
        
        # 保存测试数据
        print("\n保存测试数据...")
        crawler.save_to_csv(videos, 'data/test_videos.csv')
        print("✓ 已保存到 data/test_videos.csv")
        
        return True
    else:
        print("✗ 采集失败")
        return False


def main():
    """主函数"""
    print("\n🧪 B站API测试工具\n")
    
    results = []
    
    # 测试1: 搜索
    results.append(("搜索API", test_search()))
    
    # 测试2: 视频详情
    results.append(("视频详情API", test_video_info()))
    
    # 测试3: 完整采集
    results.append(("完整采集流程", test_crawl()))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    for name, success in results:
        status = "✓ 通过" if success else "✗ 失败"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 所有测试通过！API工作正常")
        print("\n下一步:")
        print("  1. 运行 'python crawl.py' 开始采集数据")
        print("  2. 运行 'python run.py' 生成图谱")
    else:
        print("\n⚠️  部分测试失败，请检查:")
        print("  1. 网络连接是否正常")
        print("  2. B站API是否可访问")
        print("  3. 是否被限流（请稍后重试）")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试中断")
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
