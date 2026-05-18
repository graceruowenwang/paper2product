# 论文发现流程

## 目标

每周投入 1-2 小时，筛选出 3-5 篇值得深入解读的论文。

---

## 信息源清单

### 每日必看（5 分钟快速扫）

1. **arXiv daily（cs.AI + cs.CL + cs.LG）**
   - 地址：https://arxiv.org/list/cs.AI/recent
   - 关注：标题中含 "product"、"application"、"system"、"real-world" 的论文
   - 工具：arxiv-monitor.py 自动推送摘要到微信/飞书

2. **HuggingFace Daily Papers**
   - 地址：https://huggingface.co/papers
   - 优势：已有社区热度数据，高赞论文优先看

3. **Twitter/X AI 圈**
   - 关注账号：@_akhaliq, @AIatMeta, @GoogleAI, @OpenAI
   - 用列表功能单独分组，每天刷 5 分钟

### 每周必看（30 分钟）

4. **Papers With Code**
   - 地址：https://paperswithcode.com
   - 关注 SOTA 榜单变化，尤其看你关注的任务

5. **Semantic Scholar 推荐流**
   - 设置研究兴趣：machine learning, NLP, recommendation systems, AI agents
   - 系统会根据你的阅读历史推荐

6. **Reddit r/MachineLearning**
   - 地址：https://reddit.com/r/MachineLearning
   - 关注 [R] 和 [D] 帖子，找工程化讨论

### 按需查看

7. **顶会论文列表**
   - NeurIPS / ICML / ICLR / ACL / EMNLP / AAAI / CVPR
   - 会议前 1-2 个月关注 accepted papers 列表
   - 会议期间关注最佳论文

8. **大厂研究博客**
   - Google Research Blog
   - Meta AI Blog
   - Microsoft Research Blog
   - Anthropic Research

9. **Newsletter**
   - Import AI (Jack Clark)
   - The Batch (deeplearning.ai)
   - Latent Space

---

## 筛选工作流

```
发现（每日 5min）
  ↓
放入 inbox/（记录：标题、来源、一句话笔记）
  ↓
快速评估（用 topic-evaluation.md 模板打分，每周一次，30min）
  ↓
≥ 7分 → reading/ → 进入深度阅读流程
5-7分 → 标记为周报候选
< 5分 → archive/
```

## 论文 Inbox 文件命名规范

`YYYY-MM-DD_来源_论文简称.md`

示例：`2026-05-17_arxiv_rag-personalized-chat.md`

## Inbox 快速记录格式

每篇在 inbox/ 新建一个文件，内容如下：

```markdown
# 论文标题

- 发现日期：
- 来源：
- arXiv/链接：
- 一句话印象：
- 初步产品联想：
- 待评估
```
