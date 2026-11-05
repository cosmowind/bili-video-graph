# RPA数据采集指南

## 采集目标

从B站搜索结果页面采集视频信息，保存为CSV格式。

## 数据字段说明

| 字段名 | 说明 | 示例 | 获取方式 |
|--------|------|------|----------|
| bv_id | 视频BV号 | BV1234567890 | 从视频链接提取 |
| title | 视频标题 | 【讲座】某某主题 | 直接获取 |
| up_name | UP主名称 | UP主昵称 | 直接获取 |
| publish_date | 发布日期 | 2024-01-01 | 直接获取或格式化 |
| play_count | 播放数 | 10000 | 需要去除"万"等单位，转为数字 |
| coin_count | 投币数 | 500 | 需要点击进入详情页获取 |
| duration | 视频时长（秒） | 3600 | 需要转换为秒数 |
| has_subtitle | 是否有字幕 | 是/否 | 从视频详情判断 |

## 采集流程

### 1. 搜索页面采集

```
1. 打开B站搜索页：https://search.bilibili.com/all?keyword=关键词
2. 设置筛选条件：
   - 时长：30分钟以上
   - 排序：按播放量/最新
3. 循环每一页：
   a. 获取当前页所有视频的BV号
   b. 获取标题、UP主、发布日期、播放数
   c. 保存到临时列表
   d. 翻页
```

### 2. 详情页补充信息

```
对于每个BV号：
1. 访问 https://www.bilibili.com/video/{BV号}
2. 等待页面加载
3. 获取投币数（通常在视频下方）
4. 获取视频时长
5. 检查是否有字幕（CC按钮）
6. 保存数据
```

### 3. 数据清洗

```
- 播放数：将"1.2万"转为12000
- 时长：将"01:30:00"转为5400秒
- 字幕：有CC标记为"是"，否则为"否"
```

## API参考（可选）

如果RPA工具支持API调用，可以使用：

### 视频信息API
```
https://api.bilibili.com/x/web-interface/view?bvid={BV号}
```

返回JSON包含：
- title: 标题
- owner.name: UP主
- pubdate: 发布时间戳
- stat.view: 播放数
- stat.coin: 投币数
- duration: 时长（秒）

### 搜索API
```
https://api.bilibili.com/x/web-interface/search/all/v2?keyword={关键词}&duration=4
```

参数说明：
- duration=4: 60分钟以上
- duration=3: 30-60分钟
- page: 页码
- page_size: 每页数量

## 输出格式

保存为 `data/videos.csv`，使用UTF-8编码：

```csv
bv_id,title,up_name,publish_date,play_count,coin_count,duration,has_subtitle
BV1RY4y1F7pG,戴锦华：历史与人民的记忆,郑日天,2007-01-01,69507,1200,5400,否
BV1ux4y1e7Yi,【公开课】戴锦华 有钱是因为努力,李财读财,2008-03-15,574,50,3600,是
```

## 注意事项

1. 反爬虫：建议设置请求间隔（1-3秒）
2. 登录状态：某些信息需要登录才能获取
3. 数据验证：检查必填字段是否完整
4. 增量采集：可以记录已采集的BV号，避免重复

## 测试数据

项目已包含 `data/videos_sample.csv` 作为示例，可以先用它测试流程。
