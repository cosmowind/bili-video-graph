#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件：自定义图谱样式和行为
"""

# 文件路径配置
PATHS = {
    'input_csv': 'data/videos.csv',
    'output_json': 'data/graph_data.json',
    'template': 'templates/graph_template.html',
    'output_html': 'output/graph.html'
}

# 节点样式配置
NODE_STYLES = {
    'Core': {
        'color': {'background': '#FF6B6B', 'border': '#C92A2A'},
        'size': 65,
        'shape': 'dot'
    },
    'Video': {
        'color': {'background': '#4ECDC4', 'border': '#1E88E5'},
        'size_min': 20,
        'size_max': 50,
        'size_factor': 1000,  # 播放量除以此值来计算节点大小
        'shape': 'dot',
        'border_with_subtitle': {'color': '#4CAF50', 'width': 2},
        'border_no_subtitle': {'color': '#1E88E5', 'width': 1}
    },
    'UP': {
        'color': {'background': '#95E1D3', 'border': '#38A169'},
        'size': 30,
        'shape': 'dot'
    }
}

# 边样式配置
EDGE_STYLES = {
    'core_to_up': {
        'width': 2,
        'color': {'opacity': 0.6},
        'dashes': False
    },
    'up_to_video': {
        'width': 1,
        'color': {'opacity': 0.4},
        'dashes': False
    },
    'video_to_video': {
        'width': 0.5,
        'color': {'opacity': 0.2},
        'dashes': True
    }
}

# 物理引擎配置
PHYSICS_CONFIG = {
    'enabled': True,
    'stabilization': {
        'enabled': True,
        'iterations': 200
    },
    'barnesHut': {
        'gravitationalConstant': -8000,
        'springConstant': 0.04,
        'springLength': 95,
        'damping': 0.09
    }
}

# 交互配置
INTERACTION_CONFIG = {
    'hover': True,
    'tooltipDelay': 200,
    'hideEdgesOnDrag': True,
    'navigationButtons': False,
    'keyboard': True
}

# 核心节点配置
CORE_NODE = {
    'id': 'core',
    'label': '核心主题',
    'title': '核心主题节点'
}

# 标题长度限制
TITLE_MAX_LENGTH = 20

# 是否创建视频间的连接（同一UP主）
CREATE_VIDEO_CONNECTIONS = True

# 连接度数（邻居高亮的层级）
HIGHLIGHT_DEGREES = 2
