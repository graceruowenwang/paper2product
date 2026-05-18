# AI PM 必读论文清单

> 基于 [Sebastian Raschka 2024 精选](https://magazine.sebastianraschka.com/p/ai-research-papers-2024-part-1)、[100 Must-Read GenAI Papers](https://thenuancedperspective.substack.com/p/100-must-read-generative-ai-papers)、[OpenAI 社区推荐](https://community.openai.com/t/foundational-must-read-gpt-llm-papers/197003)、[Awesome Agent Papers](https://github.com/luo-junyu/awesome-agent-papers)、[HuggingFace Trending](https://huggingface.co/papers/trending) 等多个来源综合整理。
>
> 按产品化价值分为三个优先级。标记 [已写] 的表示 Paper2Product 已有文章。

---

## P0：基础必读（理解 AI 产品的地基）

理解了这些论文，你就理解了 ChatGPT / Claude / Gemini 的底层逻辑。

| # | 论文 | 核心贡献 | 产品价值 | 状态 |
|---|------|---------|---------|------|
| 1 | **Attention Is All You Need** (2017) | Transformer 架构，所有 LLM 的基石 | 理解注意力机制 = 理解 LLM 的核心 | [已写]（在5步阅读法文章中） |
| 2 | **Language Models are Few-Shot Learners** (GPT-3, 2020) | 展示了 LLM 的涌现能力 | Prompt Engineering 的理论基础 | 待写 |
| 3 | **Training language models to follow instructions with human feedback** (InstructGPT, 2022) | RLHF 对齐方法 | 理解为什么 ChatGPT 比 GPT-3 好用 | 待写 |
| 4 | **Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks** (RAG, 2020) | RAG 方法论 | 企业 AI 最核心的基础能力 | 待写 |
| 5 | **Chain-of-Thought Prompting Elicits Reasoning in LLMs** (2022) | 思维链提示 | 让 AI 做复杂推理的核心技巧 | 待写 |
| 6 | **ReAct: Synergizing Reasoning and Acting in Language Models** (2023) | 推理+行动的 Agent 框架 | AI Agent 的基础范式 | 待写 |

---

## P1：当前热门（2024-2026，产品化价值最高）

这些是你公众号的主力选题方向，读者最关心、搜索流量最大。

### Agent 与工具调用

| # | 论文 | 核心贡献 | 产品价值 | 状态 |
|---|------|---------|---------|------|
| 7 | **Toolformer: Language Models Can Teach Themselves to Use Tools** (2023) | 模型自主学习使用工具 | AI Agent 工具调用的理论基础 | 待写 |
| 8 | **Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory** (2025) | 生产级长期记忆架构 | 解决 AI 没记忆的痛点 | [已写] |
| 9 | **Hermes 3 Technical Report** (2024) | 开源模型里最强的工具调用 | 私有化 Agent 的最优选择 | [已写] |
| 10 | **Are Tools All We Need? Unveiling the Tool-Use Tax in LLM Agents** (2026) | 工具调用的隐性代价 | 帮 PM 做"加不加工具"的决策 | 待写 |
| 11 | **To Call or Not to Call: Framework to Assess LLM Tool Calling** (2026) | 工具调用评估框架 | 优化 Agent 的工具调用策略 | 待写 |
| 12 | **AgentFloor: How Far Can Small Models Go on Tool Use?** (2026) | 小模型的工具调用能力边界 | 边缘部署 Agent 的可行性 | 待写 |

### RAG 与检索

| # | 论文 | 核心贡献 | 产品价值 | 状态 |
|---|------|---------|---------|------|
| 13 | **Agentic RAG: A Survey on Agentic Retrieval-Augmented Generation** (2025) | Agentic RAG 综述 | RAG 的下一代架构 | 待写 |
| 14 | **RAG-Anything: All-in-One RAG Framework** (2025) | 多模态 RAG 统一框架 | 一个框架处理文本/图片/表格 | 待写 |
| 15 | **LightRAG: Simple and Fast RAG** (2024) | 图增强的高效 RAG | 轻量级 RAG 方案 | 待写 |

### 训练与对齐

| # | 论文 | 核心贡献 | 产品价值 | 状态 |
|---|------|---------|---------|------|
| 16 | **DeepSeek-R1** (2025) | 纯 RL 训练推理能力 + 蒸馏 | 推理模型的低成本实现 | [已写]（在5步阅读法文章中） |
| 17 | **Direct Preference Optimization** (DPO, 2023) | 不需要 RL 的对齐方法 | 简化模型微调流程 | 待写 |
| 18 | **Self-Supervised Prompt Optimization** (2025) | 自监督 Prompt 优化 | 降低 Prompt 工程的成本 | 待写 |

### 评估与安全

| # | 论文 | 核心贡献 | 产品价值 | 状态 |
|---|------|---------|---------|------|
| 19 | **LLM-as-a-Judge** 评估方法 | 用 LLM 评估 LLM 输出 | AI 产品质量保障的核心手段 | 待写 |
| 20 | **Agent READMEs: Empirical Study of Context Files for Agentic Coding** (2025) | 分析 2303 个 Agent 配置文件 | 为什么 AI 编程助手经常写出烂代码 | 待写 |
| 21 | **Your Brain on ChatGPT** (2025) | AI 对认知能力的影响 | AI 产品的伦理思考 | [已写]（在5步阅读法文章中） |

---

## P2：值得关注（前沿方向，差异化选题）

写这些不容易撞题，适合形成你独特的内容风格。

| # | 论文 | 核心贡献 | 产品价值 | 状态 |
|---|------|---------|---------|------|
| 22 | **World Action Models** (2026) | 统一预测与行动的世界模型 | 机器人/具身智能的基础 | 待写 |
| 23 | **MolmoAct2: Action Reasoning Models** (2026) | 开源机器人动作推理 | 低成本机器人控制 | 待写 |
| 24 | **Self-Distilled Agentic RL** (SDAR, 2026) | Agent 训练的新 RL 方法 | 提升 Agent 训练效率 | 待写 |
| 25 | **LTX-2: Joint Audio-Visual Foundation Model** (2026) | 音视频联合生成 | 内容创作工具的基础 | 待写 |

---

## 长期追踪的信息源

| 来源 | 链接 | 用途 |
|------|------|------|
| HuggingFace Daily Papers | https://huggingface.co/papers | 每日最新论文 |
| HuggingFace Trending | https://huggingface.co/papers/trending | 持续热门论文 |
| Papers With Code | https://paperswithcode.com | SOTA 榜单变化 |
| Prompt Engineering Guide | https://promptingguide.ai/papers | Prompt 相关论文 |
| Awesome Agent Papers | https://github.com/luo-junyu/awesome-agent-papers | Agent 论文合集 |
| LLM-Agents-Papers | https://github.com/AGI-Edgerunners/LLM-Agents-Papers | Agent 论文合集 |
| Sebastian Raschka Blog | https://magazine.sebastianraschka.com | 年度论文精选 |
| @_akhaliq (Twitter) | https://x.com/_akhaliq | 每日论文速递 |

---

## 本文参考来源

- [Sebastian Raschka - Noteworthy AI Research Papers of 2024](https://magazine.sebastianraschka.com/p/ai-research-papers-2024-part-1)
- [100 Must-Read Generative AI Papers from 2024](https://thenuancedperspective.substack.com/p/100-must-read-generative-ai-papers)
- [OpenAI Community - Foundational Must-Read Papers](https://community.openai.com/t/foundational-must-read-gpt-llm-papers/197003)
- [Awesome Agent Papers (GitHub)](https://github.com/luo-junyu/awesome-agent-papers)
- [LLM-Agents-Papers (GitHub)](https://github.com/AGI-Edgerunners/LLM-Agents-Papers)
- [12 AI Agent Research Papers - LinkedIn](https://www.linkedin.com/posts/stasbel_12-research-papers-every-ai-engineer-should-activity-7422248275380154368-iY7h)
- [Best of 2025 AI Papers for Agents - LinkedIn](https://www.linkedin.com/posts/emilielundblad_best-of-2025-ai-papers-for-agents-and-real-activity-7410606129770168320-jbIy)
- [9 RAG Architectures - Towards AI](https://pub.towardsai.net/9-rag-architectures-every-ai-developer-must-master-in-2025-2f086aea6a58)
- [Prompt Engineering Guide Papers](https://www.promptingguide.ai/papers)
- [AI Papers to Read in 2025 - Towards Data Science](https://towardsdatascience.com/ai-papers-to-read-in-2025/)
