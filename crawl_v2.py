#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式采集工具 V2 - 直接生成图谱数据
"""

from src.bilibili_crawler_v2 import BilibiliCrawlerV2


def print_banner():
    """打印横幅"""
    print("=" * 60)
    print("B站视频采集工具 V2 - 图谱数据专用版")
    print("=" * 60)
    print()


def get_bv_list_from_user():
    """从用户输入获取BV号列表"""
    print("请输入BV号列表（每行一个，输入空行结束）:")
    print("示例: BV1234567890")
    print()
    
    bv_list = []
    while True:
        line = input().strip()
        if not line:
            break
        
        # 提取BV号
        if line.startswith('BV'):
            bv_list.append(line)
        elif line.startswith('http'):
            # 从URL中提取BV号
            if 'BV' in line:
                bv_id = line.split('BV')[1].split('/')[0].split('?')[0]
                bv_list.append('BV' + bv_id)
        else:
            print(f"  ⚠ 无效格式: {line}")
    
    return bv_list


def read_bv_list_from_file(file_path):
    """从文件读取BV号列表"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        bv_list = []
        for line in lines:
            line = line.strip()
            if line.startswith('BV'):
                bv_list.append(line)
            elif 'BV' in line:
                # 尝试提取BV号
                parts = line.split('BV')
                if len(parts) > 1:
                    bv_id = 'BV' + parts[1].split()[0].split(',')[0].split(')')[0]
                    bv_list.append(bv_id)
        
        return bv_list
    except FileNotFoundError:
        print(f"✗ 文件不存在: {file_path}")
        return []
    except Exception as e:
        print(f"✗ 读取文件失败: {e}")
        return []


def main():
    """主函数"""
    print_banner()
    
    # 选择采集模式
    print("请选择采集模式:")
    print("1. 手动输入BV号列表")
    print("2. 从文件读取BV号列表")
    print("3. 关键词搜索（开发中）")
    print()
    
    mode = input("请输入选项 (1-3): ").strip()
    print()
    
    crawler = BilibiliCrawlerV2()
    bv_list = []
    keyword = ""
    
    if mode == '1':
        # 手动输入
        bv_list = get_bv_list_from_user()
        if not bv_list:
            print("✗ 未输入任何BV号")
            return
        
        keyword = input("\n请输入核心关键词（用于图谱标题）: ").strip()
        if not keyword:
            keyword = "视频合集"
        
        print(f"\n共输入 {len(bv_list)} 个BV号")
        
    elif mode == '2':
        # 从文件读取
        file_path = input("请输入文件路径: ").strip()
        bv_list = read_bv_list_from_file(file_path)
        
        if not bv_list:
            print("✗ 未找到任何BV号")
            return
        
        keyword = input("\n请输入核心关键词（用于图谱标题）: ").strip()
        if not keyword:
            keyword = "视频合集"
        
        print(f"\n从文件中读取到 {len(bv_list)} 个BV号")
        
    elif mode == '3':
        # 关键词搜索
        print("⚠ 关键词搜索功能开发中...")
        print("提示: 由于B站搜索API限制，建议使用模式1或2")
        return
        
    else:
        print("✗ 无效选项")
        return
    
    # 确认采集
    print("\n准备采集:")
    print(f"  - 视频数量: {len(bv_list)}")
    print(f"  - 核心关键词: {keyword}")
    print()
    
    confirm = input("确认开始采集? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        return
    
    # 设置延迟
    delay = input("\n请求延迟（秒，建议1-2，直接回车使用默认值1）: ").strip()
    delay = float(delay) if delay else 1.0
    
    print()
    print("=" * 60)
    
    # 开始采集
    crawler.batch_get_videos(bv_list, delay=delay)
    
    # 显示统计
    print("\n" + "=" * 60)
    print("采集统计:")
    print("=" * 60)
    
    stats = crawler.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 保存数据
    print("\n" + "=" * 60)
    print("保存数据:")
    print("=" * 60)
    
    # 保存图谱JSON（主要格式）
    crawler.save_graph_json(keyword, 'data/graph_data_v2.json')
    
    # 保存CSV（兼容旧版）
    save_csv = input("\n是否同时保存CSV格式? (y/n): ").strip().lower()
    if save_csv == 'y':
        crawler.save_csv('data/videos.csv')
    
    print("\n" + "=" * 60)
    print("✓ 采集完成！")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 运行 'python run_v2.py' 生成图谱")
    print("  2. 打开 'output/graph_v2.html' 查看结果")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✗ 用户中断")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
