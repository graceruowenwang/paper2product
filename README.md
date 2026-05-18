# Paper2Product — 论文到产品

微信公众号内容项目：AI 产品经理视角，解读最具产品价值的前沿 AI/CS 论文。

## 核心理念

不是学术解读，是**产品判断**。每篇论文都要回答一个问题：**这能做什么产品？对谁有价值？**

`pm_angle_generator.py` 接入 DeepSeek API，为每篇论文生成一句话产品化角度——「公共事业SaaS」而不是「PM视角」，「企业知识库引擎」而不是「产品机会」。

## 项目目录

```
paper2product/
├── README.md                    # 本文件
├── automation/                  # 自动化工具
│   ├── arxiv-monitor.py         # arXiv 论文监控（主入口）
│   ├── pm_angle_generator.py    # PM 视角 LLM 生成（DeepSeek）
│   ├── email-digest.py          # 邮件推送
│   ├── paper-summarizer.py      # 论文摘要生成
│   ├── templates.py             # WeChat Markdown + HTML 邮件模板 + Tag 分类引擎
│   └── requirements.txt         # Python 依赖
├── prompts/                     # AI 辅助 Prompt 集合
│   ├── extract-key-info.md      # 提取论文关键信息
│   ├── draft-article.md         # 生成文章初稿
│   ├── optimize-title.md        # 优化标题
│   ├── generate-abstract.md     # 生成摘要/导语
│   └── paper-to-article.md      # 论文→文章全链路
├── templates/                   # 内容模板
│   ├── paper-review.md          # 单篇论文解读
│   ├── weekly-digest.md         # 周报
│   ├── topic-evaluation.md      # 选题评估
│   └── monthly-review.md        # 月度复盘
├── workflows/                   # 工作流文档
│   ├── discovery.md             # 论文发现流程
│   ├── reading-research.md      # 阅读与研究流程
│   ├── writing.md               # 写作流程（含 AI Prompt 链）
│   └── publishing-checklist.md  # 排版与发布检查清单
├── brand/                       # 品牌与设计系统
│   ├── guidelines.md            # 品牌视觉规范
│   ├── cover-image-prompts.md   # 首图生成 Prompt
│   ├── wechat-setup.md          # 公众号配置指南
│   └── notion-setup.md          # Notion 配置
├── operations/                  # 运营体系
│   ├── content-calendar.md      # 内容日历
│   ├── growth-strategy.md       # 增长与互动策略
│   ├── kpi-dashboard.md         # KPI 定义与复盘方法
│   └── ai-pm-must-reads.md      # AI PM 必读清单
├── editorial-calendar/          # 编辑日历实例
│   └── 2026-Q2.md               # 当前季度计划
└── papers/                      # 论文管理（看板式）
    ├── inbox/                   # 新发现的论文
    ├── digests/                 # HTML 邮件存档
    ├── done/                    # 已完成文章
    └── youtube/                 # YouTube 论文解读字幕
```

## 自动化工具

### arxiv-monitor.py — 论文监控主入口

```bash
# 基本用法：WeChat Markdown 格式输出
python automation/arxiv-monitor.py

# 完整参数
python automation/arxiv-monitor.py \
  --days 3          # 回溯天数（默认 3）
  --max 100         # 最大结果数（默认 100）
  --min-signals 3   # 最少命中信号数（默认 3，只存精读级）
  --max-show 8      # WeChat 消息中最多展示篇数（默认 8）
  --pm-angle        # 调用 DeepSeek 生成产品化角度
  --output wechat   # 输出格式：wechat / text / email
  --dry-run         # 只显示不保存
```

### pm_angle_generator.py — PM 视角生成

为每篇论文调用 DeepSeek API，生成 10 字以内的产品化角度：

```bash
# 单篇测试
python automation/pm_angle_generator.py "论文标题" "论文摘要"

# 批量模式通过 arxiv-monitor.py --pm-angle 触发
```

API key 从 `~/.hermes/.env` 读取 `DEEPSEEK_API_KEY`，也支持环境变量。

### 过滤机制：双重信号

论文需要同时满足关键词 + 产品信号才能入库：

| 层级 | 来源 | 示例 |
|------|------|------|
| 关键词 | 25 个产品导向词 | agent, rag, tool use, fine-tuning… |
| 产品信号 | 12 个落地指标 | open source, demo, SOTA, production… |

`--min-signals` 控制阈值：
- `2` → ~15 篇（宽漏斗，适合选题阶段）
- `3` → ~8 篇（默认，精读级别）
- `4` → ~3 篇（极严，只看最强信号）

### Tag 分类引擎

`templates.py` 内置 `classify_tags()`，自动为论文打 ≤5 个领域标签：

Agent · RAG · Fine-tuning · 多模态 · 推理 · 评估 · 安全 · 向量搜索 · 代码生成 · 知识图谱 · 工具调用 · 人机交互

### 输出格式

| 格式 | 用途 | 说明 |
|------|------|------|
| `wechat` | 微信通知 | Markdown 卡片，移动端优化，每行 ≤30 字 |
| `email` | HTML 邮件 | 精美卡片式邮件，支持 yeah.net / wukong 双 SMTP |
| `text` | 调试 | 纯文本原始输出 |

### 邮件推送

SMTP 双通道配置（`templates.py` 内）：

| 通道 | 发件人 | 用途 |
|------|--------|------|
| yeah.net | Product Lens \<ruowenwang@yeah.net\> | 日常推送 |
| wukong | Product Lens \<account@wukong-editor.com\> | 品牌邮件 |

## 工作原则

1. **产品视角优先**：每篇解读必须回答「这能做什么产品？对谁有价值？」
2. **AI 提效最大化**：用 AI 处理信息提取、初稿生成、标题优化，人只做判断和润色
3. **可持续节奏**：每周 2 篇深度 + 1 期周报，不追求日更
4. **复利积累**：每篇内容都是知识库的一部分，支持未来检索和复用

## 依赖

```bash
pip install -r automation/requirements.txt
```

需要 DeepSeek API key（`--pm-angle` 时使用）：写入 `~/.hermes/.env` 的 `DEEPSEEK_API_KEY=sk-...`
