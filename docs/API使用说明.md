# B站API使用说明

## 概述

本项目使用B站公开的Web API进行数据采集，无需登录即可获取视频基本信息。

## 可用API

### 1. 搜索API

**接口地址**: `https://api.bilibili.com/x/web-interface/search/type`

**请求方式**: GET

**参数说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| search_type | string | 是 | 搜索类型，固定为 "video" |
| keyword | string | 是 | 搜索关键词 |
| page | int | 否 | 页码，从1开始，默认1 |
| page_size | int | 否 | 每页数量，最大50，默认20 |
| order | string | 否 | 排序方式，见下表 |
| duration | int | 否 | 时长筛选，见下表 |

**排序方式 (order)**:

| 值 | 说明 |
|----|------|
| totalrank | 综合排序（默认） |
| click | 播放量排序 |
| pubdate | 最新发布 |
| dm | 弹幕数排序 |
| stow | 收藏数排序 |

**时长筛选 (duration)**:

| 值 | 说明 |
|----|------|
| 0 | 全部时长（默认） |
| 1 | 10分钟以下 |
| 2 | 10-30分钟 |
| 3 | 30-60分钟 |
| 4 | 60分钟以上 |

**返回示例**:

```json
{
  "code": 0,
  "message": "0",
  "data": {
    "page": 1,
    "pagesize": 20,
    "numResults": 1000,
    "result": [
      {
        "type": "video",
        "id": 123456,
        "author": "UP主名称",
        "title": "视频标题",
        "description": "视频简介",
        "arcurl": "https://www.bilibili.com/video/BV1xx411c7mD",
        "bvid": "BV1xx411c7mD",
        "play": 10000,
        "video_review": 100,
        "favorites": 500,
        "duration": "30:00",
        "pubdate": 1609459200
      }
    ]
  }
}
```

### 2. 视频详情API

**接口地址**: `https://api.bilibili.com/x/web-interface/view`

**请求方式**: GET

**参数说明**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| bvid | string | 是 | 视频BV号 |

或者使用:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| aid | int | 是 | 视频AV号 |

**返回示例**:

```json
{
  "code": 0,
  "message": "0",
  "data": {
    "bvid": "BV1xx411c7mD",
    "aid": 123456,
    "videos": 1,
    "tid": 36,
    "tname": "知识",
    "copyright": 1,
    "pic": "http://i0.hdslb.com/bfs/archive/xxx.jpg",
    "title": "视频标题",
    "pubdate": 1609459200,
    "ctime": 1609459200,
    "desc": "视频简介",
    "duration": 1800,
    "owner": {
      "mid": 123456,
      "name": "UP主名称",
      "face": "http://i0.hdslb.com/bfs/face/xxx.jpg"
    },
    "stat": {
      "aid": 123456,
      "view": 10000,
      "danmaku": 100,
      "reply": 50,
      "favorite": 500,
      "coin": 200,
      "share": 50,
      "like": 1000
    },
    "subtitle": {
      "allow_submit": false,
      "list": []
    }
  }
}
```

## 使用方法

### 方法1: 使用交互式脚本（推荐）

```bash
python crawl.py
```

按照提示选择采集模式和参数。

### 方法2: 使用Python代码

```python
from src.bilibili_crawler import BilibiliCrawler

# 创建采集器
crawler = BilibiliCrawler()

# 方式1: 根据关键词采集
videos = crawler.crawl_by_keyword(
    keyword="戴锦华",
    max_pages=3,
    duration=4,  # 60分钟以上
    order='totalrank'
)

# 方式2: 根据BV号列表采集
bvids = ['BV1RY4y1F7pG', 'BV1ux4y1e7Yi']
videos = crawler.crawl_by_bvids(bvids)

# 保存数据
crawler.save_to_csv(videos, 'data/videos.csv')
crawler.save_to_json(videos, 'data/videos.json')
```

### 方法3: 直接调用API

```python
import requests

# 搜索视频
url = 'https://api.bilibili.com/x/web-interface/search/type'
params = {
    'search_type': 'video',
    'keyword': '戴锦华',
    'page': 1,
    'duration': 4
}
response = requests.get(url, params=params)
data = response.json()

# 获取视频详情
url = 'https://api.bilibili.com/x/web-interface/view'
params = {'bvid': 'BV1RY4y1F7pG'}
response = requests.get(url, params=params)
data = response.json()
```

## 数据字段说明

采集器会将API返回的数据转换为标准格式：

| 字段 | 说明 | 来源 |
|------|------|------|
| bv_id | 视频BV号 | data.bvid |
| title | 视频标题 | data.title |
| up_name | UP主名称 | data.owner.name |
| publish_date | 发布日期 | data.pubdate (转换) |
| play_count | 播放数 | data.stat.view |
| coin_count | 投币数 | data.stat.coin |
| duration | 视频时长（秒） | data.duration |
| has_subtitle | 是否有字幕 | data.subtitle.list |
| like_count | 点赞数 | data.stat.like |
| favorite_count | 收藏数 | data.stat.favorite |
| share_count | 分享数 | data.stat.share |
| danmaku_count | 弹幕数 | data.stat.danmaku |
| desc | 视频简介 | data.desc |

## 注意事项

### 1. 请求频率限制

- 建议请求间隔 ≥ 1秒
- 避免短时间内大量请求
- 使用合理的User-Agent

### 2. 数据准确性

- API返回的数据可能有延迟
- 播放量等数据会实时变化
- 部分视频可能因权限问题无法获取

### 3. 反爬虫策略

B站有基本的反爬虫机制：

- **User-Agent检测**: 必须设置合理的User-Agent
- **Referer检测**: 建议设置Referer为bilibili.com
- **频率限制**: 请求过快可能被限制
- **IP限制**: 同一IP短时间大量请求可能被封

**应对策略**:

```python
# 设置合理的请求头
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://www.bilibili.com'
}

# 添加请求间隔
import time
time.sleep(1.5)  # 每次请求间隔1.5秒

# 使用代理（可选）
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'https://proxy.example.com:8080'
}
```

### 4. 错误处理

常见错误码：

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| 0 | 成功 | - |
| -400 | 请求错误 | 检查参数 |
| -404 | 视频不存在 | 跳过该视频 |
| -412 | 请求被拦截 | 降低请求频率 |
| 62002 | 稿件不可见 | 跳过该视频 |

### 5. 合法合规

- 仅用于学习和研究目的
- 不要用于商业用途
- 尊重UP主版权
- 遵守B站用户协议

## 高级用法

### 1. 批量采集多个关键词

```python
keywords = ['戴锦华', '电影理论', '文化研究']
all_videos = []

for keyword in keywords:
    videos = crawler.crawl_by_keyword(keyword, max_pages=2)
    all_videos.extend(videos)
    time.sleep(5)  # 关键词间延迟

crawler.save_to_csv(all_videos)
```

### 2. 增量更新

```python
import pandas as pd

# 读取已有数据
existing_df = pd.read_csv('data/videos.csv')
existing_bvids = set(existing_df['bv_id'])

# 采集新数据
new_videos = crawler.crawl_by_keyword('戴锦华', max_pages=1)

# 过滤已存在的视频
new_videos = [v for v in new_videos if v['bv_id'] not in existing_bvids]

# 追加保存
if new_videos:
    new_df = pd.DataFrame(new_videos)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
    combined_df.to_csv('data/videos.csv', index=False, encoding='utf-8-sig')
```

### 3. 自定义筛选

```python
# 只保留播放量大于1万的视频
videos = crawler.crawl_by_keyword('戴锦华', max_pages=5)
filtered_videos = [v for v in videos if v['play_count'] > 10000]
crawler.save_to_csv(filtered_videos)
```

## 参考资源

- [B站API文档（非官方）](https://github.com/SocialSisterYi/bilibili-API-collect)
- [uapis.cn B站API](https://uapis.cn/docs/api-reference/get-social-bilibili-videoinfo)
- [B站开放平台](https://open.bilibili.com/)

## 常见问题

### Q: 为什么有些视频获取不到？

A: 可能原因：
- 视频已被删除或下架
- 视频设置了权限（仅粉丝可见等）
- 视频在审核中
- API返回错误

### Q: 如何提高采集速度？

A: 
- 适当减小请求间隔（但不要低于0.5秒）
- 使用多线程（需要注意频率限制）
- 使用代理池

### Q: 数据不完整怎么办？

A: 
- 检查网络连接
- 增加请求超时时间
- 查看日志了解具体错误
- 重新采集失败的视频

---

**最后更新**: 2026-03-04
