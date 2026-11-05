#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站采集器 V2 - 直接输出图谱格式
"""

import requests
import time
import json
from datetime import datetime
from pathlib import Path


class BilibiliCrawlerV2:
    """B站视频采集器 - 直接生成图谱数据格式"""
    
    def __init__(self):
        self.base_url = "https://uapis.cn/api/biliinfo"
        self.videos = []
        self.ups = {}
        
    def search_videos(self, keyword, max_count=100, delay=1):
        """
        搜索视频并采集数据
        
        Args:
            keyword: 搜索关键词
            max_count: 最大采集数量
            delay: 请求延迟（秒）
        """
        print(f"开始搜索关键词: {keyword}")
        print(f"目标数量: {max_count}")
        
        # 这里需要实现搜索逻辑
        # 由于B站搜索API可能有限制，这里提供框架
        
        collected = 0
        page = 1
        
        while collected < max_count:
            print(f"\n正在采集第 {page} 页...")
            
            # TODO: 实现搜索API调用
            # 这里需要根据实际的搜索API来实现
            
            # 示例：假设我们有BV号列表
            # bv_list = self._search_page(keyword, page)
            
            # for bv_id in bv_list:
            #     if collected >= max_count:
            #         break
            #     
            #     video_data = self.get_video_info(bv_id)
            #     if video_data:
            #         self.videos.append(video_data)
            #         collected += 1
            #     
            #     time.sleep(delay)
            
            page += 1
            
            # 防止无限循环
            if page > 10:
                break
        
        print(f"\n采集完成！共采集 {len(self.videos)} 个视频")
        return self
    
    def get_video_info(self, bv_id):
        """
        获取单个视频信息
        
        Args:
            bv_id: 视频BV号
            
        Returns:
            dict: 视频信息字典，符合图谱数据格式
        """
        try:
            url = f"{self.base_url}?bv={bv_id}"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                print(f"  ✗ {bv_id}: HTTP {response.status_code}")
                return None
            
            data = response.json()
            
            if data.get('code') != 200:
                print(f"  ✗ {bv_id}: API错误 {data.get('msg', 'Unknown')}")
                return None
            
            info = data['data']
            
            # 提取UP主信息
            up_mid = str(info['owner']['mid'])
            up_name = info['owner']['name']
            
            # 存储UP主信息
            if up_mid not in self.ups:
                self.ups[up_mid] = {
                    'mid': up_mid,
                    'name': up_name,
                    'videos': []
                }
            
            self.ups[up_mid]['videos'].append(bv_id)
            
            # 构建视频数据（符合图谱格式）
            video_data = {
                'bv_id': bv_id,
                'title': info['title'],
                'desc': info.get('desc', ''),
                'cover_url': info.get('pic', ''),
                'play_count': info['stat']['view'],
                'like_count': info['stat'].get('like', 0),
                'coin_count': info['stat']['coin'],
                'favorite_count': info['stat']['favorite'],
                'share_count': info['stat']['share'],
                'danmaku_count': info['stat'].get('danmaku', 0),
                'comment_count': info['stat'].get('reply', 0),
                'duration': info.get('duration', 0),
                'publish_date': datetime.fromtimestamp(info['pubdate']).strftime('%Y-%m-%d'),
                'has_subtitle': info.get('subtitle', {}).get('list', []) != [],
                'up_name': up_name,
                'up_mid': up_mid
            }
            
            print(f"  ✓ {bv_id}: {info['title'][:30]}... (播放: {info['stat']['view']:,})")
            
            return video_data
            
        except requests.exceptions.Timeout:
            print(f"  ✗ {bv_id}: 请求超时")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  ✗ {bv_id}: 网络错误 - {e}")
            return None
        except Exception as e:
            print(f"  ✗ {bv_id}: 解析错误 - {e}")
            return None
    
    def batch_get_videos(self, bv_list, delay=1):
        """
        批量获取视频信息
        
        Args:
            bv_list: BV号列表
            delay: 请求延迟（秒）
        """
        print(f"开始批量采集 {len(bv_list)} 个视频...")
        
        for i, bv_id in enumerate(bv_list, 1):
            print(f"\n[{i}/{len(bv_list)}]")
            video_data = self.get_video_info(bv_id)
            
            if video_data:
                self.videos.append(video_data)
            
            if i < len(bv_list):
                time.sleep(delay)
        
        print(f"\n采集完成！成功: {len(self.videos)}/{len(bv_list)}")
        return self
    
    def to_graph_format(self, keyword):
        """
        转换为图谱数据格式
        
        Args:
            keyword: 核心关键词
            
        Returns:
            dict: 图谱数据
        """
        from src.data_processor_v2 import DataProcessorV2
        
        # 创建临时CSV
        import pandas as pd
        df = pd.DataFrame(self.videos)
        temp_csv = 'data/temp_videos.csv'
        df.to_csv(temp_csv, index=False, encoding='utf-8-sig')
        
        # 使用数据处理器转换
        processor = DataProcessorV2()
        processor.load_from_csv(temp_csv, core_keyword=keyword)
        processor.apply_edge_styles()
        
        # 删除临时文件
        Path(temp_csv).unlink(missing_ok=True)
        
        return processor.to_dict()
    
    def save_graph_json(self, keyword, output_path='data/graph_data_v2.json'):
        """
        保存为图谱JSON格式
        
        Args:
            keyword: 核心关键词
            output_path: 输出路径
        """
        graph_data = self.to_graph_format(keyword)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n图谱数据已保存: {output_path}")
        print(f"  - 节点数: {len(graph_data['nodes'])}")
        print(f"  - 边数: {len(graph_data['edges'])}")
        print(f"  - 视频数: {len(self.videos)}")
        print(f"  - UP主数: {len(self.ups)}")
        
        return self
    
    def save_csv(self, output_path='data/videos.csv'):
        """
        保存为CSV格式（兼容旧版）
        
        Args:
            output_path: 输出路径
        """
        import pandas as pd
        
        df = pd.DataFrame(self.videos)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"\nCSV数据已保存: {output_path}")
        print(f"  - 视频数: {len(self.videos)}")
        
        return self
    
    def get_statistics(self):
        """获取采集统计信息"""
        if not self.videos:
            return {}
        
        import pandas as pd
        df = pd.DataFrame(self.videos)
        
        stats = {
            'total_videos': len(self.videos),
            'total_ups': len(self.ups),
            'total_plays': int(df['play_count'].sum()),
            'avg_plays': int(df['play_count'].mean()),
            'max_plays': int(df['play_count'].max()),
            'min_plays': int(df['play_count'].min()),
            'total_likes': int(df['like_count'].sum()),
            'total_coins': int(df['coin_count'].sum()),
            'total_favorites': int(df['favorite_count'].sum()),
            'videos_with_subtitle': int(df['has_subtitle'].sum()),
            'subtitle_rate': f"{df['has_subtitle'].sum() / len(df) * 100:.1f}%"
        }
        
        return stats


def main():
    """测试函数"""
    crawler = BilibiliCrawlerV2()
    
    # 测试单个视频
    print("测试单个视频采集:")
    video = crawler.get_video_info('BV1234567890')
    
    if video:
        print("\n视频信息:")
        print(json.dumps(video, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
