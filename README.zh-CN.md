<p align="center"><img src="assets/cover.svg" alt="Podcast XMind · 播客导图：把播客变成能追溯的阅读材料" width="100%"></p>

<h1 align="center">播客导图 · Podcast XMind</h1>

<p align="center"><strong>播客积压太多？把它变成值得读完的材料。</strong><br>保留数字更正、推理、条件、反例，还有偏离主线的好话题。</p>

<p align="center">
<a href="https://github.com/zachsaws/podcast-xmind/actions/workflows/ci.yml"><img src="https://github.com/zachsaws/podcast-xmind/actions/workflows/ci.yml/badge.svg" alt="持续检查状态"></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-173C36?style=flat" alt="MIT许可"></a>
<a href="https://github.com/zachsaws/podcast-xmind/releases"><img src="https://img.shields.io/github/v/release/zachsaws/podcast-xmind?include_prereleases&color=C94C32&label=preview" alt="预览版本"></a>
</p>

<p align="center"><a href="README.md">English</a> · <a href="#开始使用">开始使用</a> · <a href="examples/synthetic/run/reading.md">看完整效果</a> · <a href="https://github.com/zachsaws/podcast-xmind/releases">下载</a></p>

给一个可取得全文的播客链接，或一份转录文件。这个 Agent Skill 会先逐段读原稿、建立信息账本，再给你三层阅读：

**2–3分钟扫读 → 按信息密度决定长度的深读 → 按需原话证据。**

有实质内容的长节目通常以15–25分钟深读为目标。短节目更短，信息密集的节目可以更长；没有固定2000字上限。

## 一处细节，可能改变整段结论

[![合成示例：1000注册、80付费；成本口径、稳定输入条件与医院反例一起保留](assets/evidence-tour.png)](examples/synthetic/run/reading.md)

图中是本项目的原创合成材料，不对应真实公司，也不是与其他工具的跑分结果。你可以核对原稿与实际输出：

| 原稿里的信息 | 阅读材料中保留的内容 |
|---|---|
| 主持人把1000理解成付费客户 | 嘉宾更正：**1000注册账户、80家付费，截至6月底** |
| 成本从2美元降到0.80美元 | 分母是**每个完成任务**，条件是输入稳定；不是模型调用价格 |
| 医院试点失败 | 输入变化大，成本反升，试点暂停 |
| 与增长无关的数据政策 | 默认训练不用用户数据、30天删除、法定日志例外 |
| “明年也许” | 保留推测及未知身份，不改成发布承诺 |

[原稿](examples/synthetic/excerpt.txt) · [实际中文阅读](examples/synthetic/run/reading.md) · [英文版](examples/synthetic/run/reading.en.md) · [账本](examples/synthetic/run/ledger.json) · [审计](examples/synthetic/run/audit.json)

<details>
<summary>看三步证据演示</summary>

![基于已保存合成示例制作的演示图，不是应用实录](assets/evidence-tour.gif)

这是根据已保存产物制作的图示演示，不是应用录屏。

</details>

## 开始使用

需要支持技能的代理；辅助工具使用 Python 3.10+ 标准库。模型、网页读取和转录能力由宿主提供，本项目不要求额外 API Key 或服务器。

```sh
git clone https://github.com/zachsaws/podcast-xmind.git
cd podcast-xmind
```

选择**一种**安装方式，避免重复入口：

| 使用环境 | 安装 | 调用 |
|---|---|---|
| ChatGPT 桌面插件 | `python3 scripts/install_plugin.py` | 重启后在 `@` 菜单的“插件”分类找「播客导图」 |
| Codex 独立技能 | `python3 scripts/install.py --agent codex` | `$podcast-xmind <链接或文件>` |
| Claude Code 技能目录 | `python3 scripts/install.py --agent claude` | `/podcast-xmind <链接或文件>` |

```text
$podcast-xmind 请把这期播客整理成中文深读：<链接或转录文件>
```

想先审查再安装，可以直接读 [SKILL.md](skills/podcast-xmind/SKILL.md) 和[完整示例](examples/synthetic/run/reading.md)。

**兼容状态：**Codex/Work 执行、桌面插件安装已验证；安装后普通 Chat 菜单显示及 Claude Code 实机执行仍待验证。本地技能不会自动成为网页插件。[完整兼容说明](docs/compatibility.md) · [非原生 Chat 备用方案](docs/chat-fallback.md)

## 你会得到什么

| 阅读层 | 内容 |
|---|---|
| **扫读** | 有用的问题、主要回答、关键限定和话题导航 |
| **深读** | 推理过程、重要数字、具体例子、反例、分歧及独立旁支 |
| **证据** | 原语言摘录、说话人、真实时间码或段落位置、未解决的疑点 |

背后的流程：**原稿 → 分段提取 → 信息账本 → 主题重组 → 双向回查**。重复表达可以合并，不同论据和条件继续保留。

真实播客案例：[NASA 第181期《Passing Down Knowledge》→中文深读](examples/nasa/run/reading.md)。保留模型适用边界、购买服务时的学习路径，以及办公室照片这个人物旁支。[来源记录](examples/nasa/README.md) · [评估证据](docs/evaluation.md)

## 哪些检查能复现

离线工具支持 TXT/MD、SRT、VTT 和片段 JSON，保留原文件、来源位置和真实字幕时间。审计检查账本重要单元是否进入正文、引语是否匹配、说话人标签是否一致，以及账目是否自洽。

```sh
python3 -m unittest discover -s tests -v
python3 scripts/verify_examples.py
```

CI 在 Python 3.10、3.12、3.13 上运行。示例检查从保留的原始文件重建片段，并重新审计实际阅读产物。[命令与数据合同](skills/podcast-xmind/references/ledger-contract.md)

**结构通过不代表信息提取完整、事实真实、译文正确或转录准确。** 语义检查仍需回到原稿。[实际评估范围](docs/evaluation.md)

## 常见问题

<details>
<summary>任何播客链接都能直接处理吗？</summary>

链接是查找入口。全文可用性受登录、地区、字幕及宿主能力影响。只有节目介绍或摘录，就只交付明确的部分覆盖结果。捆绑代码没有通用下载器或 ASR 引擎。

</details>

<details>
<summary>会生成原生 .xmind 文件吗？</summary>

当前交付是 Markdown 深读与 JSON 证据账本，尚不包含原生 `.xmind` 导出。Podcast XMind 是独立项目，与 Xmind 无隶属关系。

</details>

<details>
<summary>我的材料会上传到哪里？</summary>

辅助工具本地运行，没有遥测、云上传或模型 API 调用。宿主代理及你选择的转录服务仍按各自规则处理材料。个人运行材料放在 `runs/` 或指定私有目录，不提交到公共仓库。

</details>

## 帮它少漏掉一个好观点

最有价值的贡献是一次具体遗漏：可分享的原稿片段、实际输出，以及为什么那处细节影响理解。

[报告阅读问题](https://github.com/zachsaws/podcast-xmind/issues/new?template=omission.md) · [提出改进](https://github.com/zachsaws/podcast-xmind/issues/new?template=feature.yml) · [贡献指南](CONTRIBUTING.md) · [路线图](docs/roadmap.md)

如果它帮你读完了积压的播客，欢迎 **Star**，也欢迎分享一个别人能核对的实例。

受 [orange2ai/podcast-to-article](https://github.com/orange2ai/podcast-to-article) 的事实账本与原话核验思路启发，代码和指令独立编写，面向阅读保真。[设计记录](docs/design-notes.md) · [MIT](LICENSE) · [来源致谢](NOTICE.md)
