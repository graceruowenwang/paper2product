# Paper2Product -- 论文到产品

微信公众号内容项目：AI产品经理视角，解读最具产品价值的前沿 AI/CS 论文。

## 项目目录结构

```
paper2product/
├── README.md                    # 本文件，项目总览
├── templates/                   # 内容模板
│   ├── paper-review.md          # 单篇论文解读模板
│   ├── weekly-digest.md         # 周报模板
│   ├── topic-evaluation.md      # 选题评估模板
│   └── monthly-review.md        # 月度复盘模板
├── workflows/                   # 工作流文档
│   ├── discovery.md             # 论文发现流程
│   ├── reading-research.md      # 阅读与研究流程
│   ├── writing.md               # 写作流程（含 AI Prompt 链）
│   └── publishing-checklist.md  # 排版与发布检查清单
├── automation/                  # 自动化工具
│   ├── arxiv-monitor.py         # arXiv 论文监控脚本
│   ├── paper-summarizer.py      # 论文摘要生成脚本
│   └── requirements.txt         # Python 依赖
├── prompts/                     # AI 辅助 Prompt 集合
│   ├── extract-key-info.md      # 提取论文关键信息
│   ├── draft-article.md         # 生成文章初稿
│   ├── optimize-title.md        # 优化标题
│   └── generate-abstract.md     # 生成摘要/导语
├── brand/                       # 品牌与设计系统
│   ├── guidelines.md            # 品牌视觉规范
│   ├── cover-image-prompts.md   # 首图生成 Prompt
│   └── wechat-setup.md          # 公众号配置指南
├── operations/                  # 运营体系
│   ├── content-calendar.md      # 内容日历（前3个月）
│   ├── growth-strategy.md       # 增长与互动策略
│   └── kpi-dashboard.md         # KPI 定义与复盘方法
├── editorial-calendar/          # 编辑日历实例
│   └── 2026-Q2.md               # 当前季度计划
└── papers/                      # 论文管理（看板式）
    ├── inbox/                   # 新发现的论文
    ├── reading/                 # 正在阅读/研究
    ├── done/                    # 已完成文章
    └── archive/                 # 归档（放弃的选题等）
```

## 工作原则

1. **产品视角优先**：每篇解读必须回答"这能做什么产品？对谁有价值？"
2. **AI 提效最大化**：用 AI 处理信息提取、初稿生成、标题优化，人只做判断和润色
3. **可持续节奏**：每周 2 篇深度 + 1 期周报，不追求日更
4. **复利积累**：每篇内容都是知识库的一部分，支持未来检索和复用
