# Podcast Deep Reader · 播客深读

**读到细节，跳过冗余。把播客变成能追溯、能检查遗漏的分层阅读。**

[English](README.en.md) · [先看真实输出](examples/nasa/run/reading.md) · [3分钟理解差异](examples/synthetic/README.md) · [下载](https://github.com/zachsaws/podcast-deep-reader/releases)

![From source to layered reading, with evidence and coverage boundaries](assets/cover.svg)

播客积压时，最让人不放心的往往不是摘要太短，而是不知道它删掉了什么：一个更正过的数字、结论成立的条件、失败的试点，或者偏离主线却很有价值的独立话题。

这个 Agent Skill 先逐段建立信息账本，再按主题重组，最后回到原稿核对。默认提供 **2–3分钟扫读 → 动态篇幅深读 → 按需原话证据**。长而有料的节目通常以15–25分钟深读为目标；短节目更短，高密度节目可更长。没有统一的2000字上限。

> v0.1.0：已验证本地 Codex/Work 文件执行、独立代理示例、标准库工具和仓库示例；尚未验证 Claude Code 实机或本项目在普通 Chat 的原生 `@` 安装。结构审计通过不等于信息无遗漏。

## 先看它会保住什么

原创合成测试摘录中，主持人问“1000个付费客户是不是说明增长验证了”，嘉宾立即纠正。实际输出保留：

| 容易丢的细节 | 示例中的处理 |
|---|---|
| 数字与口径 | **1000注册账户，80家付费，截至6月底**；没有擅自算成转化率 |
| 降本机制 | 从每条都审核，改为仅审核模型不确定的请求 |
| 成本分母与条件 | **每个完成任务**从$2降到$0.80，前提是输入稳定；不是调用价格 |
| 反例 | 医院试点输入变化大，成本反升，试点暂停 |
| 独立话题 | 数据默认训练、30天删除，以及法定日志例外 |
| 不确定性 | “明年也许”保留为推测，匿名标签不升级为人物身份 |

这是可逐句核对的单次示例，**不是与其他项目跑分后的性能结论**。[原稿](examples/synthetic/excerpt.txt) / [完整阅读](examples/synthetic/run/reading.md) / [信息账本](examples/synthetic/run/ledger.json) / [实际审计](examples/synthetic/run/audit.json)。

真实跨语言案例：[NASA 第181期《Passing Down Knowledge》→中文深读](examples/nasa/run/reading.md)。取得完整发布方文字稿，保留技术机制、模型边界、采购服务的学习路径和个人旁支；不伪造原稿没有的时间码。[来源与处理记录](examples/nasa/README.md)。

## 安装与调用

需要一个能读取技能的代理。脚本另需 Python 3.10+，无需额外依赖、API Key 或本项目服务；生成内容使用你当前代理的模型与工具。

```sh
git clone https://github.com/zachsaws/podcast-deep-reader.git
cd podcast-deep-reader
python3 scripts/install.py --agent codex
```

安装到 `~/.agents/skills/podcast-deep-reader`，已有路径会拒绝覆盖。Codex 若没有刷新出新技能，开启新会话或重启。然后：

```text
$podcast-deep-reader https://某期播客链接
```

也可以直接给文件：

```text
$podcast-deep-reader 请把这份 episode.vtt 整理成中文深读，保留论据、数字与独立话题。
```

Claude Code 的目录安装：`python3 scripts/install.py --agent claude`，然后用 `/podcast-deep-reader <链接或文件>`。这符合其[官方技能目录格式](https://code.claude.com/docs/en/skills)，尚未做 Claude Code 实机验证。其他支持 [Agent Skills](https://agentskills.io/specification) 的代理可加载 `skills/podcast-deep-reader/`；能否读链接、转录音频取决于宿主。

## ChatGPT Plus 能直接 @ 吗？

**官方现在有 `@` 技能机制；这不等于本仓库已经在你的普通 Chat 中安装。** 截至2026-10-16，[官方 Build skills](https://learn.chatgpt.com/docs/build-skills) 写明 ChatGPT 使用 `@`，Codex 使用 `$`，跨网页/桌面/移动的分发途径是插件；[官方定价功能表](https://learn.chatgpt.com/docs/pricing) 把 Plus 的 Skills 和 Plugins 标为可用。具体账号、版本、工作区和安装入口仍需实际确认。

本项目提供三条路径，状态明确区分：

| 路径 | 本项目提供什么 | 验证状态 |
|---|---|---|
| 本地 Codex / Work | 完整技能目录、安装器和离线辅助工具 | 已执行验证 |
| Chat 原生 `@` | `plugin.json`、仓库 marketplace、技能ZIP和插件ZIP | 已打包；未上架目录、未在目标账号安装验证 |
| 无原生安装入口的 Chat | [项目指令与每次输入备用方案](docs/chat-fallback.md) | 手动提示工作流，**不是原生技能或插件** |

具体安装入口、官方资料口径差异与目标账号验收步骤见[兼容性说明](docs/compatibility.md)。在本机复制技能不会自动同步到网页；把仓库链接发到 Chat 也不会自动安装插件。不要只因订阅 Plus 就假定已经具备自定义安装入口。

## 一个链接会发生什么

1. 找发布方全文，或取得可访问的完整字幕；必要时用宿主已有转录工具。
2. 明确是完整文字稿、部分文字、只有节目介绍，还是没有可读内容。
3. 分段阅读，建立“主张—说话人—原文片段—位置”账本，记录每段是否审阅。
4. 合并重复观点，保留不同论据、修正、反例和独立话题，生成分层阅读。
5. 运行结构审计，再人工语义回查原稿，交付阅读与明确的覆盖边界。

**不是所有链接都能取得全文。** 小宇宙、Apple Podcasts、Spotify、YouTube 等页面只是入口，登录、地区、反爬、字幕和宿主能力可能限制读取。捆绑代码没有通用下载器、ASR引擎或付费服务调用。只拿到节目介绍，就只交付节目介绍范围内的材料；不冒充“已听完整期”。

## 离线工具：辅助代理，不替代模型

```sh
# 支持 TXT/MD、SRT、VTT、segments JSON；保留原文件与时间码
python3 skills/podcast-deep-reader/scripts/pdr.py prepare episode.vtt \
  --out runs/episode --scope partial --scope-note '用户提供的字幕摘录'

# 代理填好 ledger.json、写好 reading.md 后运行
python3 skills/podcast-deep-reader/scripts/pdr.py audit \
  runs/episode/transcript.json runs/episode/ledger.json runs/episode/reading.md \
  --out runs/episode/audit.json
```

没有模型API调用。`prepare` 不会自动完成深读；`audit` 不会替你判断主张真伪。命令、数据格式与退出码见[账本合同](skills/podcast-deep-reader/references/ledger-contract.md)。所有个人录音和运行材料放在 `runs/` 或用户指定目录，不提交进仓库。

## 可以验证什么

```sh
python3 -m unittest discover -s tests -v
python3 scripts/verify_examples.py
python3 scripts/package.py --out dist
```

- 测试涵盖时间码、字幕说话人、中文与JSON、分块守恒、拒绝静默丢弃、原文件哈希、引语不匹配、人物错归、遗漏单元、部分覆盖、拒绝覆盖安装与可复现打包。
- 示例验证重新从原稿生成规范化片段，并重新审计已提交的真实阅读产物。
- GitHub Actions 在 Python 3.10、3.12、3.13 运行相同检查；当前结果看 [Actions](https://github.com/zachsaws/podcast-deep-reader/actions)。

审计能发现：账目不一致、引语找不到、说话人标签不一致、重要单元没进入深读、某主题未保留、原稿意外变动。它**不能证明**：原始信息都被提取了、引语确实支持主张、重要性评估正确、译文准确、音频转录无错或节目陈述真实。报告的单元覆盖数字只以代理建立的账本为分母。[评估方法与不足](docs/evaluation.md)。

## 参与与后续

最有价值的贡献是一个可复现的遗漏：带授权的原稿片段、丢失的信息、实际输出和应保留的原因。[贡献指南](CONTRIBUTING.md)包含隐私与复现要求。计划优先验证长节目、多人争论和中英混合材料，再决定是否增加来源适配器。

如果它帮助你读到了原本会丢的内容，欢迎 Star 或分享具体案例。项目不宣称节省比例、准确率、用户规模，也不保证 Star 数量；[公开传播计划](docs/launch.md)围绕可检查的示例与反馈展开。

## 致谢与许可

受到 [orange2ai/podcast-to-article](https://github.com/orange2ai/podcast-to-article) 的事实账本与原话核验思路启发。本项目目标是阅读保真与覆盖透明，不沿用其单一主线和固定篇幅规则；代码与指令重新编写。[参考项目阅读记录](docs/design-notes.md)。

原创代码、指令与合成示例采用 [MIT](LICENSE)。NASA 来源文字保留其原有地位和使用条件，见 [NOTICE](NOTICE.md)；NASA、OpenAI、Anthropic 均未为本项目背书。
