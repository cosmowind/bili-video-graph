#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图谱生成脚本：使用模板生成交互式HTML图谱
"""

import json
from pathlib import Path
from jinja2 import Template

class GraphGenerator:
    def __init__(self, data_path='data/graph_data.json', template_path='src/graph_template.html'):
        self.data_path = data_path
        self.template_path = template_path
        self.data = None
        
    def load_data(self):
        """加载图谱数据"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        print(f"加载了 {len(self.data['nodes'])} 个节点和 {len(self.data['edges'])} 条边")
        return self
    
    def generate_html(self, output_path='output/graph.html'):
        """生成HTML文件"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = Template(f.read())
        
        # 准备节点选项
        node_options = []
        for node in self.data['nodes']:
            if node['group'] in ['Video', 'UP']:
                node_options.append({
                    'value': node['id'],
                    'label': node['label']
                })
        
        html_content = template.render(
            nodes=json.dumps(self.data['nodes'], ensure_ascii=False),
            edges=json.dumps(self.data['edges'], ensure_ascii=False),
            node_options=node_options
        )
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"图谱已生成: {output_path}")
        return self

def main():
    generator = GraphGenerator()
    generator.load_data().generate_html()
    print("图谱生成完成！")

if __name__ == '__main__':
    main()
