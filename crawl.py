#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站视频采集工具 - 交互式命令行界面
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from bilibili_crawler import BilibiliCrawler


def print_banner():
    """打印欢迎信息"""
    print("=" * 60)
    print("  B站视频信息采集工具")
    print("=" * 60)
    print()


def get_duration_choice():
    """获取时长筛选选项"""
    print("请选择视频时长筛选:")
    print("  0 - 全部时长")
    print("  1 - 10分钟以下")
    print("  2 - 10-30分钟")
    print("  3 - 30-60分钟")
    print("  4 - 60分钟以上")
    
    while True:
        choice = input("请输入选项 (0-4，默认0): ").strip()
        if not choice:
            return 0
        if choice in ['0', '1', '2', '3', '4']:
            return int(choice)
        print("❌ 无效选项，请重新输入")


def get_order_choice():
    """获取排序方式选项"""
    print("\n请选择排序方式:")
    print("  1 - 综合排序")
    print("  2 - 播放量排序")
    print("  3 - 最新发布")
    print("  4 - 弹幕数排序")
    print("  5 - 收藏数排序")
    
    order_map = {
        '1': 'totalrank',
        '2': 'click',
        '3': 'pubdate',
        '4': 'dm',
        '5': 'stow'
    }
    
    while True:
        choice = input("请输入选项 (1-5，默认1): ").strip()
        if not choice:
            return 'totalrank'
        if choice in order_map:
            return order_map[choice]
        print("❌ 无效选项，请重新输入")


def crawl_by_keyword():
    """根据关键词采集"""
    print("\n" + "=" * 60)
    print("  模式1: 根据关键词搜索采集")
    print("=" * 60)
    
    # 获取关键词
    keyword = input("\n请输入搜索关键词: ").strip()
    if not keyword:
        print("❌ 关键词不能为空")
        return
    
    # 获取采集页数
    while True:
        pages_input = input("请输入采集页数 (1-10，默认3): ").strip()
        if not pages_input:
            max_pages = 3
            break
        try:
            max_pages = int(pages_input)
            if 1 <= max_pages <= 10:
                break
            print("❌ 页数必须在1-10之间")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    # 获取时长筛选
    duration = get_duration_choice()
    
    # 获取排序方式
    order = get_order_choice()
    
    # 获取请求间隔
    while True:
        delay_input = input("\n请输入请求间隔秒数 (0.5-5，默认1.5): ").strip()
        if not delay_input:
            delay = 1.5
            break
        try:
            delay = float(delay_input)
            if 0.5 <= delay <= 5:
                break
            print("❌ 间隔必须在0.5-5秒之间")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    # 确认信息
    print("\n" + "-" * 60)
    print("采集配置:")
    print(f"  关键词: {keyword}")
    print(f"  页数: {max_pages}")
    print(f"  时长筛选: {['全部', '10分钟以下', '10-30分钟', '30-60分钟', '60分钟以上'][duration]}")
    print(f"  排序方式: {order}")
    print(f"  请求间隔: {delay}秒")
    print("-" * 60)
    
    confirm = input("\n确认开始采集? (y/n，默认y): ").strip().lower()
    if confirm and confirm != 'y':
        print("❌ 已取消采集")
        return
    
    # 开始采集
    print("\n🚀 开始采集...\n")
    crawler = BilibiliCrawler()
    videos = crawler.crawl_by_keyword(
        keyword=keyword,
        max_pages=max_pages,
        duration=duration,
        order=order,
        delay=delay
    )
    
    # 保存数据
    if videos:
        print("\n💾 保存数据...")
        crawler.save_to_csv(videos, 'data/videos.csv')
        crawler.save_to_json(videos, 'data/videos.json')
        print("\n✅ 采集完成！")
        print(f"   CSV文件: data/videos.csv")
        print(f"   JSON文件: data/videos.json")
        print(f"   共采集 {len(videos)} 个视频")
    else:
        print("\n❌ 未采集到任何数据")


def crawl_by_bvids():
    """根据BV号列表采集"""
    print("\n" + "=" * 60)
    print("  模式2: 根据BV号列表采集")
    print("=" * 60)
    
    print("\n请输入BV号列表（每行一个，输入空行结束）:")
    print("示例: BV1RY4y1F7pG")
    print()
    
    bvids = []
    while True:
        bvid = input("BV号: ").strip()
        if not bvid:
            break
        if bvid.startswith('BV'):
            bvids.append(bvid)
            print(f"  ✓ 已添加: {bvid}")
        else:
            print("  ❌ 无效的BV号（应以BV开头）")
    
    if not bvids:
        print("❌ 没有输入任何BV号")
        return
    
    # 获取请求间隔
    while True:
        delay_input = input("\n请输入请求间隔秒数 (0.5-5，默认1.0): ").strip()
        if not delay_input:
            delay = 1.0
            break
        try:
            delay = float(delay_input)
            if 0.5 <= delay <= 5:
                break
            print("❌ 间隔必须在0.5-5秒之间")
        except ValueError:
            print("❌ 请输入有效的数字")
    
    # 确认信息
    print("\n" + "-" * 60)
    print(f"将采集 {len(bvids)} 个视频:")
    for idx, bvid in enumerate(bvids, 1):
        print(f"  {idx}. {bvid}")
    print(f"请求间隔: {delay}秒")
    print("-" * 60)
    
    confirm = input("\n确认开始采集? (y/n，默认y): ").strip().lower()
    if confirm and confirm != 'y':
        print("❌ 已取消采集")
        return
    
    # 开始采集
    print("\n🚀 开始采集...\n")
    crawler = BilibiliCrawler()
    videos = crawler.crawl_by_bvids(bvids, delay=delay)
    
    # 保存数据
    if videos:
        print("\n💾 保存数据...")
        crawler.save_to_csv(videos, 'data/videos.csv')
        crawler.save_to_json(videos, 'data/videos.json')
        print("\n✅ 采集完成！")
        print(f"   CSV文件: data/videos.csv")
        print(f"   JSON文件: data/videos.json")
        print(f"   成功采集 {len(videos)}/{len(bvids)} 个视频")
    else:
        print("\n❌ 未采集到任何数据")


def main():
    """主函数"""
    print_banner()
    
    print("请选择采集模式:")
    print("  1 - 根据关键词搜索采集")
    print("  2 - 根据BV号列表采集")
    print("  0 - 退出")
    print()
    
    choice = input("请输入选项 (0-2): ").strip()
    
    if choice == '1':
        crawl_by_keyword()
    elif choice == '2':
        crawl_by_bvids()
    elif choice == '0':
        print("👋 再见！")
        return
    else:
        print("❌ 无效选项")
        return
    
    # 询问是否生成图谱
    print("\n" + "=" * 60)
    generate = input("是否立即生成图谱? (y/n，默认n): ").strip().lower()
    if generate == 'y':
        print("\n🎨 生成图谱中...")
        import subprocess
        result = subprocess.run([sys.executable, 'run.py'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 图谱生成完成！请打开 output/graph.html 查看")
        else:
            print("❌ 图谱生成失败")
            print(result.stderr)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
