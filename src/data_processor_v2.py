#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理器 V2 - 基于JSON配置的可复用版本
"""

import json
import math
import pandas as pd
from pathlib import Path
from datetime import datetime


class DataProcessorV2:
    """基于JSON配置的数据处理器"""
    
    def __init__(self, config_path='config/node_config.json', schema_path='config/graph_schema.json'):
        self.config_path = config_path
        self.schema_path = schema_path
        self.config = self._load_config()
        self.schema = self._load_schema()
        self.nodes = []
        self.edges = []
        self.metadata = {}
        
    def _load_config(self):
        """加载节点配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_schema(self):
        """加载数据格式规范"""
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_from_csv(self, csv_path, core_keyword=None):
        """
        从CSV文件加载数据并转换为图谱格式
        
        Args:
            csv_path: CSV文件路径
            core_keyword: 核心关键词（可选）
        """
        df = pd.read_csv(csv_path)
        
        # 提取核心关键词
        if core_keyword is None:
            core_keyword = self._extract_keyword(df)
        
        # 创建核心节点
        self._create_core_node(core_keyword)
        
        # 创建视频和UP主节点
        self._create_video_nodes(df, core_keyword)
        
        # 生成元数据
        self._generate_metadata(df, core_keyword)
        
        return self
    
    def load_from_json(self, json_path):
        """
        从JSON文件加载图谱数据
        
        Args:
            json_path: JSON文件路径
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.nodes = data.get('nodes', [])
        self.edges = data.get('edges', [])
        self.metadata = data.get('metadata', {})
        
        return self
    
    def _extract_keyword(self, df):
        """从数据中提取核心关键词"""
        # 简单实现：从第一个视频标题中提取
        if len(df) > 0:
            title = df.iloc[0]['title']
            # 可以使用更复杂的关键词提取算法
            return title.split()[0] if title else "视频合集"
        return "视频合集"
    
    def _create_core_node(self, keyword):
        """创建核心节点"""
        core_config = self.config['node_types']['Core']
        
        node = {
            'id': keyword,
            'label': keyword,
            'group': 'Core',
            'title': f'核心主题：{keyword}',
            'shape': core_config['shape'],
            'size': core_config['size'],
            'color': core_config['color'],
            'font': core_config['font']
        }
        
        self.nodes.append(node)
    
    def _create_video_nodes(self, df, core_keyword):
        """创建视频和UP主节点"""
        video_config = self.config['node_types']['Video']
        up_config = self.config['node_types']['UP']
        
        up_set = set()
        
        for _, row in df.iterrows():
            bv_id = row['bv_id']
            up_name = row['up_name']
            up_mid = str(row.get('up_mid', ''))
            up_id = f"UP_{up_mid}" if up_mid else f"UP_{up_name}"
            
            # 计算视频节点大小
            play_count = row['play_count']
            size = self._calculate_node_size(
                play_count,
                video_config['size_min'],
                video_config['size_max'],
                df['play_count'].min(),
                df['play_count'].max(),
                video_config.get('size_scale', 'linear')
            )
            
            # 判断是否有字幕
            has_subtitle = row.get('has_subtitle', '无') in ['有', True, 'true', '是']
            
            # 选择颜色配置
            color = video_config['color_subtitle'] if has_subtitle else video_config['color']
            
            # 创建视频节点
            video_node = {
                'id': bv_id,
                'label': row['title'][:20] + '...' if len(row['title']) > 20 else row['title'],
                'group': 'Video',
                'title': f"{row['title']}\n播放: {play_count:,}",
                'shape': video_config['shape'],
                'size': size,
                'value': play_count,
                'color': color,
                'font': video_config['font'],
                'metadata': {
                    'play_count': int(play_count),
                    'like_count': int(row.get('like_count', 0)),
                    'coin_count': int(row['coin_count']),
                    'favorite_count': int(row.get('favorite_count', 0)),
                    'share_count': int(row.get('share_count', 0)),
                    'danmaku_count': int(row.get('danmaku_count', 0)),
                    'comment_count': int(row.get('comment_count', 0)),
                    'publish_date': str(row['publish_date']),
                    'duration': int(row.get('duration', 0)),
                    'has_subtitle': has_subtitle,
                    'desc': str(row.get('desc', ''))[:200],
                    'up_name': up_name,
                    'up_mid': up_mid
                }
            }
            
            self.nodes.append(video_node)
            
            # 创建核心到视频的边
            self.edges.append({
                'from': core_keyword,
                'to': bv_id,
                'type': 'core_to_video'
            })
            
            # 创建UP主节点（去重）
            if up_id not in up_set:
                up_set.add(up_id)
                up_node = {
                    'id': up_id,
                    'label': up_name,
                    'group': 'UP',
                    'title': f'UP主: {up_name}',
                    'shape': up_config['shape'],
                    'size': up_config['size'],
                    'color': up_config['color'],
                    'font': up_config['font']
                }
                self.nodes.append(up_node)
            
            # 创建视频到UP主的边
            self.edges.append({
                'from': bv_id,
                'to': up_id,
                'type': 'video_to_up'
            })
    
    def _calculate_node_size(self, value, min_size, max_size, min_value, max_value, scale='linear'):
        """
        计算节点大小
        
        Args:
            value: 当前值
            min_size: 最小尺寸
            max_size: 最大尺寸
            min_value: 数据最小值
            max_value: 数据最大值
            scale: 缩放方式 ('linear' 或 'log')
        """
        if max_value == min_value:
            return (min_size + max_size) / 2
        
        if scale == 'log':
            # 对数缩放
            log_value = math.log(value + 1)
            log_min = math.log(min_value + 1)
            log_max = math.log(max_value + 1)
            normalized = (log_value - log_min) / (log_max - log_min)
        else:
            # 线性缩放
            normalized = (value - min_value) / (max_value - min_value)
        
        return min_size + normalized * (max_size - min_size)
    
    def _generate_metadata(self, df, keyword):
        """生成图谱元数据"""
        self.metadata = {
            'title': f'{keyword}视频关系图谱',
            'description': f'基于B站搜索关键词"{keyword}"的视频关系可视化',
            'created_at': datetime.now().isoformat(),
            'source': 'bilibili',
            'keyword': keyword,
            'total_videos': len(df),
            'total_ups': df['up_name'].nunique(),
            'total_plays': int(df['play_count'].sum())
        }
    
    def add_lecture_series(self, series_name, video_ids):
        """
        添加讲座系列节点
        
        Args:
            series_name: 系列名称
            video_ids: 属于该系列的视频BV号列表
        """
        lecture_config = self.config['node_types']['Lecture']
        
        # 创建讲座系列节点
        lecture_node = {
            'id': f'LECTURE_{series_name}',
            'label': series_name,
            'group': 'Lecture',
            'title': f'讲座系列: {series_name}',
            'shape': lecture_config['shape'],
            'size': lecture_config['size'],
            'color': lecture_config['color'],
            'font': lecture_config['font']
        }
        
        self.nodes.append(lecture_node)
        
        # 创建系列到视频的边
        for video_id in video_ids:
            self.edges.append({
                'from': f'LECTURE_{series_name}',
                'to': video_id,
                'type': 'lecture_to_video'
            })
    
    def add_reference(self, ref_name, ref_type, related_videos):
        """
        添加参考文献节点
        
        Args:
            ref_name: 参考文献名称
            ref_type: 文献类型（书籍、论文等）
            related_videos: 相关视频BV号列表
        """
        ref_config = self.config['node_types']['Reference']
        
        # 创建参考文献节点
        ref_node = {
            'id': f'REF_{ref_name}',
            'label': ref_name,
            'group': 'Reference',
            'title': f'{ref_type}: {ref_name}',
            'shape': ref_config['shape'],
            'size': ref_config['size'],
            'color': ref_config['color'],
            'font': ref_config['font']
        }
        
        self.nodes.append(ref_node)
        
        # 创建视频到参考文献的边
        for video_id in related_videos:
            self.edges.append({
                'from': video_id,
                'to': f'REF_{ref_name}',
                'type': 'video_to_reference'
            })
    
    def apply_edge_styles(self):
        """应用边的样式配置"""
        edge_types = self.config['edge_types']
        
        for edge in self.edges:
            edge_type = edge.get('type', 'video_to_up')
            if edge_type in edge_types:
                style = edge_types[edge_type]
                edge.update({
                    'color': style['color'],
                    'width': style['width'],
                    'arrows': style.get('arrows', ''),
                    'smooth': style.get('smooth', {}),
                    'dashes': style.get('dashes', False)
                })
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'metadata': self.metadata
        }
    
    def save_json(self, output_path):
        """保存为JSON文件"""
        data = self.to_dict()
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"图谱数据已保存: {output_path}")
        print(f"  - 节点数: {len(self.nodes)}")
        print(f"  - 边数: {len(self.edges)}")
        print(f"  - 视频数: {self.metadata.get('total_videos', 0)}")
        print(f"  - UP主数: {self.metadata.get('total_ups', 0)}")
        
        return self
    
    def get_statistics(self):
        """获取统计信息"""
        stats = {
            'nodes': {
                'total': len(self.nodes),
                'by_type': {}
            },
            'edges': {
                'total': len(self.edges),
                'by_type': {}
            },
            'metadata': self.metadata
        }
        
        # 统计节点类型
        for node in self.nodes:
            group = node['group']
            stats['nodes']['by_type'][group] = stats['nodes']['by_type'].get(group, 0) + 1
        
        # 统计边类型
        for edge in self.edges:
            edge_type = edge.get('type', 'unknown')
            stats['edges']['by_type'][edge_type] = stats['edges']['by_type'].get(edge_type, 0) + 1
        
        return stats


def main():
    """测试函数"""
    processor = DataProcessorV2()
    
    # 从CSV加载数据
    processor.load_from_csv('data/videos.csv', core_keyword='站桩')
    
    # 应用边样式
    processor.apply_edge_styles()
    
    # 保存JSON
    processor.save_json('data/graph_data_v2.json')
    
    # 打印统计信息
    stats = processor.get_statistics()
    print("\n统计信息:")
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
