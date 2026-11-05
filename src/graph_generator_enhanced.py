#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版图谱生成器 - 包含侧边栏和排行榜
"""

import json
from pathlib import Path
from jinja2 import Template
import pandas as pd


class EnhancedGraphGenerator:
    def __init__(self, data_path='data/graph_data.json', csv_path='data/videos.csv'):
        self.data_path = data_path
        self.csv_path = csv_path
        self.data = None
        self.video_details = {}
        self.rankings = {}
        
    def load_data(self):
        """加载图谱数据"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"加载了 {len(self.data['nodes'])} 个节点和 {len(self.data['edges'])} 条边")
        return self
    
    def load_video_details(self):
        """加载视频详细信息"""
        df = pd.read_csv(self.csv_path)
        
        for _, row in df.iterrows():
            desc = row.get('desc', '')
            if pd.isna(desc) or not isinstance(desc, str):
                desc = ''
            
            self.video_details[row['bv_id']] = {
                'title': row['title'],
                'up': row['up_name'],
                'date': str(row['publish_date']),
                'views': f"{row['play_count']:,}",
                'likes': f"{row.get('like_count', 0):,}",
                'coins': f"{row['coin_count']:,}",
                'favs': f"{row.get('favorite_count', 0):,}",
                'subtitle': row['has_subtitle'],
                'desc': desc[:200] if desc else ''
            }
        
        print(f"加载了 {len(self.video_details)} 个视频详情")
        return self
    
    def calculate_rankings(self):
        """计算各种排行榜"""
        df = pd.read_csv(self.csv_path)
        
        # 播放量排行
        views_rank = df.nlargest(10, 'play_count')[['bv_id', 'title', 'play_count']].to_dict('records')
        self.rankings['views'] = [
            {
                'title': r['title'][:30] + '...' if len(r['title']) > 30 else r['title'],
                'bvid': r['bv_id'],
                'val': f"{r['play_count']:,}"
            }
            for r in views_rank
        ]
        
        # 点赞率排行（点赞/播放）
        df['like_rate'] = df.get('like_count', 0) / df['play_count'] * 100
        likes_rank = df.nlargest(10, 'like_rate')[['bv_id', 'title', 'like_rate']].to_dict('records')
        self.rankings['likes'] = [
            {
                'title': r['title'][:30] + '...' if len(r['title']) > 30 else r['title'],
                'bvid': r['bv_id'],
                'val': f"{r['like_rate']:.2f}%"
            }
            for r in likes_rank
        ]
        
        # 投币率排行（投币/播放）
        df['coin_rate'] = df['coin_count'] / df['play_count'] * 100
        coins_rank = df.nlargest(10, 'coin_rate')[['bv_id', 'title', 'coin_rate']].to_dict('records')
        self.rankings['coins'] = [
            {
                'title': r['title'][:30] + '...' if len(r['title']) > 30 else r['title'],
                'bvid': r['bv_id'],
                'val': f"{r['coin_rate']:.2f}%"
            }
            for r in coins_rank
        ]
        
        # 综合转化率（点赞+投币+收藏）/播放
        df['conv_rate'] = (
            df.get('like_count', 0) + 
            df['coin_count'] + 
            df.get('favorite_count', 0)
        ) / df['play_count'] * 100
        conv_rank = df.nlargest(10, 'conv_rate')[['bv_id', 'title', 'conv_rate']].to_dict('records')
        self.rankings['conv'] = [
            {
                'title': r['title'][:30] + '...' if len(r['title']) > 30 else r['title'],
                'bvid': r['bv_id'],
                'val': f"{r['conv_rate']:.2f}%"
            }
            for r in conv_rank
        ]
        
        print(f"计算了 4 种排行榜")
        return self
    
    def generate_html(self, output_path='output/graph_enhanced.html'):
        """生成增强版HTML文件"""
        template_path = Path(__file__).parent / 'graph_template_enhanced.html'
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        # 准备节点选项
        node_options = []
        for node in self.data['nodes']:
            if node['group'] in ['Video', 'UP']:
                node_options.append({
                    'value': node['id'],
                    'label': node['label']
                })
        
        # 统计信息
        video_count = len([n for n in self.data['nodes'] if n['group'] == 'Video'])
        
        html_content = template.render(
            nodes=json.dumps(self.data['nodes'], ensure_ascii=False),
            edges=json.dumps(self.data['edges'], ensure_ascii=False),
            node_options=node_options,
            video_details=json.dumps(self.video_details, ensure_ascii=False),
            rankings=json.dumps(self.rankings, ensure_ascii=False),
            video_count=video_count
        )
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"增强版图谱已生成: {output_path}")
        return self


def main():
    """主函数"""
    generator = EnhancedGraphGenerator()
    generator.load_data().load_video_details().calculate_rankings().generate_html()
    print("增强版图谱生成完成！")


if __name__ == '__main__':
    main()
