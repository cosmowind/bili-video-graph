# V1 vs V2 版本对比

## 快速对比表

| 特性 | V1版本 | V2版本 |
|------|--------|--------|
| **配置方式** | 代码中硬编码 | JSON配置文件 |
| **数据格式** | CSV → 内部处理 | 标准JSON格式 |
| **节点类型** | 3种（Core, Video, UP） | 5种（+Lecture, Reference） |
| **样式修改** | 需修改代码 | 修改JSON配置 |
| **采集器对接** | 生成CSV | 直接生成图谱JSON |
| **可扩展性** | 中等 | 高 |
| **学习曲线** | 简单 | 中等 |
| **维护成本** | 高 | 低 |

## 文件对比

### V1版本文件

```
src/
├── data_processor.py          # 数据处理（样式硬编码）
├── graph_generator.py         # 基础图谱生成
├── graph_generator_enhanced.py # 增强版图谱生成
├── graph_template.html        # 基础模板
├── graph_template_enhanced.html # 增强版模板
├── bilibili_crawler.py        # 采集器（输出CSV）
└── config.py                  # 配置文件（有限）

run.py                         # 基础版运行脚本
run_enhanced.py                # 增强版运行脚本
crawl.py                       # 交互式采集工具
```

### V2版本文件

```
config/
├── node_config.json           # 节点配置（样式、物理引擎等）
└── graph_schema.json          # 数据格式规范

src/
├── data_processor_v2.py       # 数据处理器V2（配置驱动）
├── graph_generator_v2.py      # 图谱生成器V2
├── graph_template_v2.html     # 模板V2
└── bilibili_crawler_v2.py     # 采集器V2（输出JSON）

run_v2.py                      # 运行脚本V2
crawl_v2.py                    # 交互式采集工具V2
```

## 使用流程对比

### V1版本

```bash
# 1. 采集数据
python crawl.py
# 输出: data/videos.csv

# 2. 生成图谱
python run_enhanced.py
# 内部处理: CSV → 图谱数据 → HTML
# 输出: output/graph_enhanced.html
```

### V2版本

```bash
# 1. 采集数据
python crawl_v2.py
# 输出: data/graph_data_v2.json（标准格式）

# 2. 生成图谱
python run_v2.py
# 内部处理: JSON → HTML（配置驱动）
# 输出: output/graph_v2.html
```

## 代码对比

### 修改节点样式

#### V1版本
需要修改 `src/data_processor.py`：

```python
# 硬编码在代码中
node = {
    'id': bv_id,
    'label': title,
    'group': 'Video',
    'shape': 'dot',
    'size': size,
    'color': {
        'background': '#4ECDC4',
        'border': '#1E88E5'
    },
    'font': {
        'size': 14,
        'color': 'white'
    }
}
```

#### V2版本
只需修改 `config/node_config.json`：

```json
{
  "node_types": {
    "Video": {
      "shape": "dot",
      "size_min": 15,
      "size_max": 40,
      "color": {
        "background": "#4ECDC4",
        "border": "#1E88E5"
      },
      "font": {
        "size": 14,
        "color": "#ffffff"
      }
    }
  }
}
```

### 添加新节点类型

#### V1版本
需要修改多个文件：

1. `src/data_processor.py` - 添加节点创建逻辑
2. `src/graph_template_enhanced.html` - 添加CSS样式
3. `src/config.py` - 添加配置项

#### V2版本
只需修改 `config/node_config.json`：

```json
{
  "node_types": {
    "NewType": {
      "shape": "diamond",
      "size": 25,
      "color": {...},
      "font": {...}
    }
  }
}
```

然后在代码中使用：

```python
processor.add_custom_node('NewType', node_id, label, metadata)
```

## 数据格式对比

### V1版本 - CSV格式

```csv
bv_id,title,up_name,play_count,like_count,coin_count,...
BV1234567890,视频标题,UP主,10000,500,200,...
```

**问题**：
- 缺少结构化的节点和边信息
- 需要在生成时重新计算关系
- 不包含图谱元数据

### V2版本 - JSON格式

```json
{
  "nodes": [
    {
      "id": "BV1234567890",
      "label": "视频标题",
      "group": "Video",
      "metadata": {
        "play_count": 10000,
        "like_count": 500,
        ...
      }
    }
  ],
  "edges": [
    {
      "from": "BV1234567890",
      "to": "UP_123456",
      "type": "video_to_up"
    }
  ],
  "metadata": {
    "title": "图谱标题",
    "total_videos": 100,
    ...
  }
}
```

**优势**：
- 结构化存储节点和边
- 包含完整的元数据
- 易于验证和调试
- 可直接用于其他可视化工具

## 性能对比

| 指标 | V1版本 | V2版本 |
|------|--------|--------|
| **数据加载** | 需要解析CSV并重建关系 | 直接加载JSON |
| **样式应用** | 运行时计算 | 配置预加载 |
| **内存占用** | 中等 | 略高（JSON更详细） |
| **生成速度** | 快 | 快 |
| **可缓存性** | 低 | 高 |

## 扩展性对比

### V1版本

添加新功能需要：
1. 修改数据处理逻辑
2. 修改生成器代码
3. 修改HTML模板
4. 可能需要修改采集器

### V2版本

添加新功能只需：
1. 修改JSON配置（大多数情况）
2. 或添加新的处理方法（复杂功能）

## 适用场景

### 使用V1版本

适合以下场景：
- ✅ 快速原型开发
- ✅ 简单的图谱需求
- ✅ 不需要频繁修改样式
- ✅ 团队成员熟悉Python

### 使用V2版本

适合以下场景：
- ✅ 需要频繁调整样式
- ✅ 需要支持多种节点类型
- ✅ 需要与其他系统集成
- ✅ 需要数据格式标准化
- ✅ 长期维护的项目
- ✅ 多人协作开发

## 迁移建议

### 何时迁移到V2

考虑迁移如果：
- 需要频繁修改节点样式
- 需要添加新的节点类型
- 需要与其他系统对接
- 项目规模扩大
- 需要更好的可维护性

### 如何迁移

1. **数据迁移**
   ```bash
   python src/data_processor_v2.py
   ```

2. **配置迁移**
   - 将 `src/config.py` 中的配置转换为JSON
   - 保存到 `config/node_config.json`

3. **代码迁移**
   - 逐步替换导入语句
   - 测试功能是否正常

4. **并行运行**
   - V1和V2可以共存
   - 逐步切换到V2

## 兼容性

### V2向后兼容V1

- ✅ 可以读取V1的CSV数据
- ✅ 可以生成V1风格的输出
- ✅ 配置文件可选（有默认值）

### V1无法直接使用V2数据

- ❌ V1不支持JSON格式输入
- ✅ 但可以通过V2导出CSV给V1使用

## 总结

### V1版本优势
- 简单直接
- 学习曲线平缓
- 适合快速开发

### V2版本优势
- 配置驱动，易于维护
- 数据标准化，易于集成
- 高度可扩展
- 适合长期项目

### 推荐

- **新项目**：直接使用V2版本
- **现有项目**：
  - 简单需求：继续使用V1
  - 复杂需求：考虑迁移到V2
  - 可以两个版本并存

---

**最后更新**: 2026-03-04
