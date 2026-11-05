#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站视频信息采集器
使用B站公开API采集视频数据
"""

import requests
import time
import json
import csv
from pathlib import Path
from typing import List, Dict, Optional
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BilibiliCrawler:
    """B站视频信息采集器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bilibili.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Origin': 'https://www.bilibili.com'
        })
        
    def search_videos(self, keyword: str, page: int = 1, 
                     page_size: int = 20, duration: int = 0,
                     order: str = 'totalrank') -> Dict:
        """
        搜索视频
        
        Args:
            keyword: 搜索关键词
            page: 页码（从1开始）
            page_size: 每页数量（最大50）
            duration: 时长筛选 0-全部 1-10分钟以下 2-10-30分钟 3-30-60分钟 4-60分钟以上
            order: 排序方式 totalrank-综合排序 click-播放量 pubdate-最新发布 dm-弹幕数 stow-收藏数
            
        Returns:
            搜索结果字典
        """
        url = 'https://api.bilibili.com/x/web-interface/search/type'
        params = {
            'search_type': 'video',
            'keyword': keyword,
            'page': page,
            'page_size': min(page_size, 50),
            'order': order,
            'duration': duration
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            
            # 检查状态码
            if response.status_code == 412:
                logger.warning("遇到反爬虫限制(412)，建议增加请求间隔或稍后重试")
                return {}
            
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', {})
            else:
                logger.error(f"API返回错误: {data.get('message')}")
                return {}
                
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 412:
                logger.warning("遇到反爬虫限制，请稍后重试")
            else:
                logger.error(f"HTTP错误: {e}")
            return {}
        except Exception as e:
            logger.error(f"搜索请求失败: {e}")
            return {}
    
    def get_video_info(self, bvid: str) -> Optional[Dict]:
        """
        获取视频详细信息
        
        Args:
            bvid: 视频BV号
            
        Returns:
            视频信息字典
        """
        url = 'https://api.bilibili.com/x/web-interface/view'
        params = {'bvid': bvid}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0:
                return data.get('data', {})
            else:
                logger.error(f"获取视频信息失败 {bvid}: {data.get('message')}")
                return None
                
        except Exception as e:
            logger.error(f"请求失败 {bvid}: {e}")
            return None
    
    def parse_video_data(self, video_info: Dict) -> Dict:
        """
        解析视频数据为标准格式
        
        Args:
            video_info: 原始视频信息
            
        Returns:
            标准化的视频数据
        """
        # 检查是否有字幕
        has_subtitle = '否'
        if video_info.get('subtitle', {}).get('list'):
            has_subtitle = '是'
        
        # 格式化发布日期
        pubdate = video_info.get('pubdate', 0)
        if pubdate:
            from datetime import datetime
            publish_date = datetime.fromtimestamp(pubdate).strftime('%Y-%m-%d')
        else:
            publish_date = ''
        
        return {
            'bv_id': video_info.get('bvid', ''),
            'title': video_info.get('title', ''),
            'up_name': video_info.get('owner', {}).get('name', ''),
            'publish_date': publish_date,
            'play_count': video_info.get('stat', {}).get('view', 0),
            'coin_count': video_info.get('stat', {}).get('coin', 0),
            'duration': video_info.get('duration', 0),
            'has_subtitle': has_subtitle,
            'like_count': video_info.get('stat', {}).get('like', 0),
            'favorite_count': video_info.get('stat', {}).get('favorite', 0),
            'share_count': video_info.get('stat', {}).get('share', 0),
            'danmaku_count': video_info.get('stat', {}).get('danmaku', 0),
            'desc': video_info.get('desc', '')[:100]  # 简介截取前100字
        }
    
    def crawl_by_keyword(self, keyword: str, max_pages: int = 5,
                        duration: int = 0, order: str = 'totalrank',
                        delay: float = 1.0) -> List[Dict]:
        """
        根据关键词批量采集视频
        
        Args:
            keyword: 搜索关键词
            max_pages: 最大采集页数
            duration: 时长筛选
            order: 排序方式
            delay: 请求间隔（秒）
            
        Returns:
            视频数据列表
        """
        all_videos = []
        
        logger.info(f"开始采集关键词: {keyword}")
        logger.info(f"采集页数: {max_pages}, 时长筛选: {duration}, 排序: {order}")
        
        for page in range(1, max_pages + 1):
            logger.info(f"正在采集第 {page}/{max_pages} 页...")
            
            # 搜索视频
            search_result = self.search_videos(
                keyword=keyword,
                page=page,
                duration=duration,
                order=order
            )
            
            if not search_result:
                logger.warning(f"第 {page} 页搜索失败，跳过")
                continue
            
            result_list = search_result.get('result', [])
            if not result_list:
                logger.info(f"第 {page} 页没有更多结果")
                break
            
            logger.info(f"第 {page} 页找到 {len(result_list)} 个视频")
            
            # 获取每个视频的详细信息
            for idx, item in enumerate(result_list, 1):
                bvid = item.get('bvid')
                if not bvid:
                    continue
                
                logger.info(f"  [{idx}/{len(result_list)}] 获取视频详情: {bvid}")
                
                video_info = self.get_video_info(bvid)
                if video_info:
                    video_data = self.parse_video_data(video_info)
                    all_videos.append(video_data)
                    logger.info(f"    ✓ {video_data['title'][:30]}...")
                
                # 延迟避免请求过快
                time.sleep(delay)
            
            # 页面间延迟
            if page < max_pages:
                time.sleep(delay * 2)
        
        logger.info(f"采集完成！共获取 {len(all_videos)} 个视频")
        return all_videos
    
    def crawl_by_bvids(self, bvids: List[str], delay: float = 1.0) -> List[Dict]:
        """
        根据BV号列表批量采集视频
        
        Args:
            bvids: BV号列表
            delay: 请求间隔（秒）
            
        Returns:
            视频数据列表
        """
        all_videos = []
        
        logger.info(f"开始采集 {len(bvids)} 个视频...")
        
        for idx, bvid in enumerate(bvids, 1):
            logger.info(f"[{idx}/{len(bvids)}] 获取视频: {bvid}")
            
            video_info = self.get_video_info(bvid)
            if video_info:
                video_data = self.parse_video_data(video_info)
                all_videos.append(video_data)
                logger.info(f"  ✓ {video_data['title'][:30]}...")
            else:
                logger.warning(f"  ✗ 获取失败")
            
            time.sleep(delay)
        
        logger.info(f"采集完成！成功获取 {len(all_videos)}/{len(bvids)} 个视频")
        return all_videos
    
    def save_to_csv(self, videos: List[Dict], output_path: str = 'data/videos.csv'):
        """
        保存视频数据到CSV文件
        
        Args:
            videos: 视频数据列表
            output_path: 输出文件路径
        """
        if not videos:
            logger.warning("没有数据可保存")
            return
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # CSV字段
        fieldnames = [
            'bv_id', 'title', 'up_name', 'publish_date',
            'play_count', 'coin_count', 'duration', 'has_subtitle',
            'like_count', 'favorite_count', 'share_count', 'danmaku_count', 'desc'
        ]
        
        with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(videos)
        
        logger.info(f"数据已保存到: {output_path}")
        logger.info(f"共保存 {len(videos)} 条记录")
    
    def save_to_json(self, videos: List[Dict], output_path: str = 'data/videos.json'):
        """
        保存视频数据到JSON文件
        
        Args:
            videos: 视频数据列表
            output_path: 输出文件路径
        """
        if not videos:
            logger.warning("没有数据可保存")
            return
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(videos, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {output_path}")


def main():
    """主函数示例"""
    crawler = BilibiliCrawler()
    
    # 示例1: 根据关键词采集
    keyword = "戴锦华"
    videos = crawler.crawl_by_keyword(
        keyword=keyword,
        max_pages=3,           # 采集3页
        duration=4,            # 60分钟以上
        order='totalrank',     # 综合排序
        delay=1.5              # 请求间隔1.5秒
    )
    
    # 保存数据
    if videos:
        crawler.save_to_csv(videos, 'data/videos.csv')
        crawler.save_to_json(videos, 'data/videos.json')
    
    # 示例2: 根据BV号列表采集
    # bvids = ['BV1RY4y1F7pG', 'BV1ux4y1e7Yi']
    # videos = crawler.crawl_by_bvids(bvids, delay=1.0)
    # crawler.save_to_csv(videos)


if __name__ == '__main__':
    main()
