# B站视频关系图谱生成器

## 项目结构

```
bili-take-tree/
├── src/                     # 核心代码
│   ├── data_processor.py   # 数据处理脚本
│   ├── graph_generator.py  # 图谱生成脚本
│   ├── graph_template.html # HTML模板
│   └── config.py           # 配置文件
├── data/                    # 数据目录
│   └── videos.csv          # RPA采集的原始数据
├── output/                  # 输出目录
│   └── graph.html          # 生成的可视化图谱
├── docs/                    # 文档目录
│   ├── README.md           # 详细说明
│   ├── 使用说明.md         # 使用指南
│   ├── RPA采集指南.md      # 数据采集指南
│   └── 项目总结.md         # 项目总结
├── ref/                     # 参考资料
│   ├── 戴锦华_侧边栏增强版图谱.html  # 原项目参考
│   └── prompt.txt          # 对话记录
├── run.py                   # 主运行脚本
├── test_demo.py            # 演示脚本
└── requirements.txt        # Python依赖
```

## 使用流程

### 1. 数据采集（RPA）
使用你的RPA工具采集B站视频数据，保存为CSV格式，包含以下字段：
- bv_id: 视频BV号
- title: 视频标题
- up_name: UP主名称
- publish_date: 发布日期
- play_count: 播放数
- coin_count: 投币数
- duration: 视频时长（秒）
- has_subtitle: 是否有字幕（是/否）

### 2. 数据处理
```bash
python run.py
```

这会调用 `src/data_processor.py` 处理数据。

### 3. 生成图谱
```bash
python run.py
```

这会调用 `src/graph_generator.py` 生成HTML图谱。

### 4. 查看结果
打开 `output/graph.html` 即可查看交互式图谱

## 功能特性

- 节点按类型分组（视频、UP主、主题系列）
- 节点大小反映播放量
- 支持搜索和筛选
- 点击节点高亮相关连接
- 双击节点跳转B站
