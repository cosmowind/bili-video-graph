#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图谱生成器 V2 - 基于JSON配置
"""

import json
from pathlib import Path
from jinja2 import Template


class GraphGeneratorV2:
    """基于JSON配置的图谱生成器"""
    
    def __init__(self, 
                 data_path='data/graph_data_v2.json',
                 config_path='config/node_config.json',
                 template_path='src/graph_template_v2.html'):
        self.data_path = data_path
        self.config_path = config_path
        self.template_path = template_path
        self.data = None
        self.config = None
        
    def load_data(self):
        """加载图谱数据"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        print(f"加载图谱数据:")
        print(f"  - 节点数: {len(self.data['nodes'])}")
        print(f"  - 边数: {len(self.data['edges'])}")
        
        if 'metadata' in self.data:
            meta = self.data['metadata']
            print(f"  - 标题: {meta.get('title', 'N/A')}")
            print(f"  - 视频数: {meta.get('total_videos', 0)}")
            print(f"  - UP主数: {meta.get('total_ups', 0)}")
        
        return self
    
    def load_config(self):
        """加载配置"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        print(f"加载配置:")
        print(f"  - 节点类型: {len(self.config['node_types'])}")
        print(f"  - 边类型: {len(self.config['edge_types'])}")
        
        return self
    
    def _clean_config(self, config):
        """清理配置：去掉vis-network不认识的自定义字段，把大小映射成scaling"""
        import copy
        cfg = copy.deepcopy(config)
        
        clean_node_types = {}
        for group_name, group_cfg in cfg.get('node_types', {}).items():
            clean = {}
            # 保留vis-network认识的字段
            allowed = {'shape', 'size', 'color', 'font', 'borderWidth', 'shadow',
                       'scaling', 'value', 'title', 'mass', 'icon', 'image'}
            for k, v in group_cfg.items():
                if k in allowed:
                    clean[k] = v
            
            # 处理大小映射
            if 'size_field' in group_cfg:
                clean['scaling'] = {
                    'min': group_cfg.get('size_min', 15),
                    'max': group_cfg.get('size_max', 40),
                    'label': {'enabled': True, 'min': 10, 'max': 20}
                }
            
            clean_node_types[group_name] = clean
        
        cfg['node_types'] = clean_node_types
        return cfg

    def generate_html(self, output_path='output/graph_v2.html'):
        """生成HTML文件"""
        template_file = Path(self.template_path)
        
        with open(template_file, 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        # 加载本地vis-network（内联，生成自包含HTML）
        vis_dir = Path(__file__).parent / 'templates'
        with open(vis_dir / 'vis-network.min.js', 'r', encoding='utf-8') as f:
            vis_js = f.read().replace('</script>', '<\\/script>')
        with open(vis_dir / 'vis-network.min.css', 'r', encoding='utf-8') as f:
            vis_css = f.read()
        
        # 清理配置
        clean_config = self._clean_config(self.config)
        
        # 准备节点选项（用于下拉框）
        node_options = []
        for node in self.data['nodes']:
            if node['group'] in ['Video', 'UP']:
                node_options.append({
                    'value': node['id'],
                    'label': node['label']
                })
        
        # 准备视频详情数据
        video_details = {}
        for node in self.data['nodes']:
            if node['group'] == 'Video' and 'metadata' in node:
                meta = node['metadata']
                video_details[node['id']] = {
                    'title': node['label'],
                    'up': meta.get('up_name', ''),
                    'date': meta.get('publish_date', ''),
                    'views': f"{meta.get('play_count', 0):,}",
                    'likes': f"{meta.get('like_count', 0):,}",
                    'coins': f"{meta.get('coin_count', 0):,}",
                    'favs': f"{meta.get('favorite_count', 0):,}",
                    'subtitle': '有' if meta.get('has_subtitle', False) else '无',
                    'desc': meta.get('desc', '')[:200]
                }
        
        # 计算排行榜
        rankings = self._calculate_rankings()
        
        # 渲染模板
        html_content = template.render(
            nodes=json.dumps(self.data['nodes'], ensure_ascii=False),
            edges=json.dumps(self.data['edges'], ensure_ascii=False),
            config=json.dumps(clean_config, ensure_ascii=False),
            metadata=json.dumps(self.data.get('metadata', {}), ensure_ascii=False),
            node_options=node_options,
            video_details=json.dumps(video_details, ensure_ascii=False),
            rankings=json.dumps(rankings, ensure_ascii=False),
            video_count=self.data.get('metadata', {}).get('total_videos', 0),
            vis_js=vis_js,
            vis_css=vis_css
        )
        
        # 保存文件
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 复制 vis-network 到输出目录
        import shutil
        vis_dir = Path(__file__).parent / 'templates'
        shutil.copy2(vis_dir / 'vis-network.min.js', output_file.parent / 'vis-network.min.js')
        shutil.copy2(vis_dir / 'vis-network.min.css', output_file.parent / 'vis-network.min.css')
        
        print(f"\n图谱已生成: {output_path}")
        
        return self
    
    def _calculate_rankings(self):
        """计算排行榜"""
        videos = []
        
        for node in self.data['nodes']:
            if node['group'] == 'Video' and 'metadata' in node:
                meta = node['metadata']
                play_count = meta.get('play_count', 0)
                like_count = meta.get('like_count', 0)
                coin_count = meta.get('coin_count', 0)
                fav_count = meta.get('favorite_count', 0)
                
                if play_count > 0:
                    videos.append({
                        'bvid': node['id'],
                        'title': node['label'],
                        'play_count': play_count,
                        'like_rate': like_count / play_count * 100,
                        'coin_rate': coin_count / play_count * 100,
                        'conv_rate': (like_count + coin_count + fav_count) / play_count * 100
                    })
        
        # 排序并取TOP 10
        rankings = {
            'views': sorted(videos, key=lambda x: x['play_count'], reverse=True)[:10],
            'likes': sorted(videos, key=lambda x: x['like_rate'], reverse=True)[:10],
            'coins': sorted(videos, key=lambda x: x['coin_rate'], reverse=True)[:10],
            'conv': sorted(videos, key=lambda x: x['conv_rate'], reverse=True)[:10]
        }
        
        # 格式化输出
        formatted = {}
        for key, items in rankings.items():
            formatted[key] = []
            for item in items:
                if key == 'views':
                    val = f"{item['play_count']:,}"
                elif key == 'likes':
                    val = f"{item['like_rate']:.2f}%"
                elif key == 'coins':
                    val = f"{item['coin_rate']:.2f}%"
                else:  # conv
                    val = f"{item['conv_rate']:.2f}%"
                
                formatted[key].append({
                    'title': item['title'][:30] + '...' if len(item['title']) > 30 else item['title'],
                    'bvid': item['bvid'],
                    'val': val
                })
        
        return formatted


def main():
    """主函数"""
    generator = GraphGeneratorV2()
    generator.load_config().load_data().generate_html()
    print("\n✓ 完成！")


if __name__ == '__main__':
    main()
