#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理脚本：将RPA采集的CSV数据转换为图谱所需的节点和边数据
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict

class DataProcessor:
    def __init__(self, csv_path='data/videos.csv'):
        self.csv_path = csv_path
        self.df = None
        self.nodes = []
        self.edges = []
        
    def load_data(self):
        """加载CSV数据"""
        self.df = pd.read_csv(self.csv_path)
        print(f"加载了 {len(self.df)} 条视频数据")
        return self
    
    def create_nodes(self):
        """创建节点数据"""
        # 创建核心节点（主题）
        core_node = {
            'id': 'core',
            'label': '站桩',
            'group': 'Core',
            'shape': 'dot',
            'size': 65,
            'font': {'color': 'white'},
            'title': '核心主题：站桩'
        }
        self.nodes.append(core_node)
        
        # 分析视频，创建主题分类
        self.create_topic_nodes()
        
        # 创建UP主节点
        up_names = self.df['up_name'].unique()
        for up_name in up_names:
            up_node = {
                'id': f'UP_{up_name}',
                'label': up_name,
                'group': 'UP',
                'shape': 'dot',
                'size': 30,
                'font': {'color': 'white'},
                'title': f'👤 UP主: {up_name}'
            }
            self.nodes.append(up_node)
        
        # 创建视频节点
        for _, row in self.df.iterrows():
            # 根据播放量计算节点大小
            size = min(50, 20 + int(row['play_count'] / 1000))
            
            # 根据是否有字幕设置边框
            border_config = {
                'borderWidth': 2,
                'borderColor': '#4CAF50'
            } if row['has_subtitle'] == '是' else {
                'borderWidth': 1,
                'borderColor': '#1E88E5'
            }
            
            video_node = {
                'id': row['bv_id'],
                'label': row['title'][:20] + '...' if len(row['title']) > 20 else row['title'],
                'group': 'Video',
                'shape': 'dot',
                'size': size,
                'font': {'color': 'white'},
                'title': f"标题: {row['title']}\nUP主: {row['up_name']}\n日期: {row['publish_date']}\n播放: {row['play_count']:,}\n投币: {row['coin_count']}\n双击跳转B站",
                **border_config
            }
            self.nodes.append(video_node)
        
        print(f"创建了 {len(self.nodes)} 个节点")
        return self
    
    def create_topic_nodes(self):
        """根据视频标题创建主题分类节点"""
        # 定义主题关键词
        topics = {
            'TOPIC_教学': ['教学', '教程', '新手', '入门', '学习', '跟练'],
            'TOPIC_理论': ['奥秘', '秘诀', '要领', '核心', '详解', '揭秘'],
            'TOPIC_实践': ['跟练', '带练', '口令', '分钟', '每天'],
            'TOPIC_养生': ['养生', '气血', '精气神', '健身', '体态']
        }
        
        # 统计每个主题的视频数量
        topic_counts = defaultdict(list)
        for _, row in self.df.iterrows():
            title = row['title']
            for topic_id, keywords in topics.items():
                if any(kw in title for kw in keywords):
                    topic_counts[topic_id].append(row['bv_id'])
        
        # 创建主题节点（至少包含3个视频才创建）
        for topic_id, video_ids in topic_counts.items():
            if len(video_ids) >= 3:
                topic_name = topic_id.replace('TOPIC_', '')
                topic_node = {
                    'id': topic_id,
                    'label': f'📚 {topic_name}',
                    'group': 'Topic',
                    'shape': 'diamond',
                    'size': 40,
                    'font': {'color': 'white'},
                    'title': f'主题分类: {topic_name}\n包含 {len(video_ids)} 个视频'
                }
                self.nodes.append(topic_node)
                
                # 记录主题关联的视频
                if not hasattr(self, 'topic_videos'):
                    self.topic_videos = {}
                self.topic_videos[topic_id] = video_ids
    
    def create_edges(self):
        """创建边数据"""
        # 核心节点连接到所有UP主
        up_names = self.df['up_name'].unique()
        for up_name in up_names:
            edge = {
                'from': 'core',
                'to': f'UP_{up_name}',
                'width': 2,
                'color': {'opacity': 0.6}
            }
            self.edges.append(edge)
        
        # UP主连接到其视频
        for _, row in self.df.iterrows():
            edge = {
                'from': f"UP_{row['up_name']}",
                'to': row['bv_id'],
                'width': 1,
                'color': {'opacity': 0.4}
            }
            self.edges.append(edge)
        
        # 同一UP主的视频之间建立连接
        up_videos = defaultdict(list)
        for _, row in self.df.iterrows():
            up_videos[row['up_name']].append(row['bv_id'])
        
        for up_name, videos in up_videos.items():
            if len(videos) > 1:
                for i in range(len(videos) - 1):
                    edge = {
                        'from': videos[i],
                        'to': videos[i + 1],
                        'width': 0.5,
                        'color': {'opacity': 0.2},
                        'dashes': True
                    }
                    self.edges.append(edge)
        
        print(f"创建了 {len(self.edges)} 条边")
        return self
    
    def save_json(self, output_path='data/graph_data.json'):
        """保存为JSON格式"""
        data = {
            'nodes': self.nodes,
            'edges': self.edges
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"数据已保存到 {output_path}")
        return self

def main():
    processor = DataProcessor('data/videos.csv')
    processor.load_data().create_nodes().create_edges().save_json()
    print("数据处理完成！")

if __name__ == '__main__':
    main()
