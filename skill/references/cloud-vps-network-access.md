# Cloud VPS 境内网络访问知识库

> 2026.06.25 通过事实核查验证。覆盖：国内主流云厂商（腾讯云、阿里云等）大陆节点对外部 API/境外网站的访问策略。
> 本文件仅记录经核实的知识，不包含推测。

## 腾讯云（本 session 验证）

### 常规公网访问

大陆节点 CVM 只要分配了弹性公网 IP（EIP）或通过 Lighthouse 自带公网 IP，就可以正常访问常规公网资源（百度、GitHub、npm/pip 镜像等）[腾讯云社区问答 2021]。

### 境外 API 访问状态

| API 提供商 | 从大陆节点访问 | 来源 |
|-----------|:-----------:|------|
| **DeepSeek** (api.deepseek.com) | ✅ 可正常直连 | Tencent Cloud 开发者教程 (2026-05-14)：「可正常直连访问 DeepSeek 官方接口 api.deepseek.com」 |
| **腾讯混元 HY** | ✅ 可正常调用 | 腾讯自家服务 |
| **GLM (智谱)** | ✅ 可正常调用 | 国内 provider |
| **Kimi (Moonshot)** | ✅ 可正常调用 | 国内 provider |
| **MiniMax CN** | ✅ 可正常调用 | 国内 provider |
| **OpenAI GPT** | ❌ 被限制 | Tencent Cloud Intl 文章 (2026-04-27)：大陆实例+海外API会被block/throttled |
| **Anthropic Claude** | ❌ 被限制 | 同上 |
| **OpenRouter** | ❌ 被限制 | 同上 |
| **Google Gemini** | ❌ 被限制 | 同上 |

**关键洞察：** DeepSeek 是中国公司（深度求索），其 API 从大陆可直接访问。不要把它归入「海外/被限制」类别。区分标准是 API 提供商国籍，而非域名后缀（.com vs .cn）。

### 香港/海外节点

腾讯云香港、新加坡、硅谷等非大陆节点可正常访问所有境外 API，包括 OpenAI/Anthropic/Google [Tencent Cloud Intl 文章 + 社区问答]。

### 腾讯云 Token Plan

腾讯云 Token Plan 套餐包含以下国内模型 [cloud.tencent.com/act/pro/hermesagent 活动页]：
- Tencent HY 2.0 Instruct
- GLM-5
- Kimi-k2.5
- MiniMax-M2.5

## Hermes Agent 部署

### Lunux（轻量应用服务器）一键部署

腾讯云 Lighthouse 已上线 Hermes Agent 专属应用镜像，选购实例时可选该镜像，自动预装所有运行环境 [cloud.tencent.com/act/pro/hermesagent]。

### 迁移

- `hermes backup` → 打包整个 ~/.hermes/（含 config, API keys, memories, skills, sessions, profiles）为 zip [Hermes FAQ]
- `hermes import` → 在新机器上恢复 [Hermes FAQ]
- `hermes profile export` / `hermes profile import` → 迁移单个 profile（不包含 credentials）[Hermes profile-commands 文档]
- `onezion-agent-sync` skill → 通过 OneDrive/git 实现持续同步

## 本 session 更正记录

| 错误 | 我写了 | 实际 |
|------|--------|------|
| DeepSeek API 可访问性 | "可能被限" | ✅ 大陆可直连 |
| 区分 CN/Global | 暗示 global 不行、CN 才行 | 实际上 api.deepseek.com 大陆直连，不存在此区分 |

## 价格 / 成本相关（2026.06.26 修正）

### HK Lighthouse 定价

| 配置 | 价格 | 来源 |
|------|:----:|------|
| 1核1G 25GB SSD 30Mbps 1TB流量 | **24元/月** | foreignserver.com 转载价格表（需在官网确认当前活动价） |
| 1核2G 50GB SSD 30Mbps 2TB流量 | **34元/月** | 同上 |
| 2核2G 80GB SSD 30Mbps 3TB流量 | **67元/月** | 同上 |

⚠️ **续费价格不可保证**：第三方博客说「续费也是24元」，但 Tencent Cloud 官方「无忧计划续费同价」有活动期限。V2EX 2023下半年已有涨价帖（v2ex.com/t/927116）。**买前检查当前是否有「续费同价」标注。**

### COS 对象存储（香港地域）

| 存储层 | 香港单价 | 来源 |
|:-------|:--------:|:-----|
| 标准存储（标准版） | **0.136元/GB/月** | 腾讯云2024年官方调价通知（cloud.tencent.com.cn/document/product/436/102430） |
| 低频存储 | 约 0.08元/GB/月 | 第三方价格表，幅度在同一通知中 |
| 归档存储 | 约 0.033元/GB/月 | 同上 |

⚠️ **常见错误**：大陆地域标准存储 ~0.099/0.118元/GB/月，容易与香港价格混淆。香港标准存储实际为 **0.136元/GB/月**（高约37%）。

### 腾讯云 ASR 语音识别免费额度

| 服务 | 免费额度/月 | 来源 |
|:-----|:----------:|:-----|
| 录音文件识别 | **10小时** | 腾讯云官方（cloud.tencent.com/document/product/1093/35693） |
| 实时语音识别 | **5小时** | 同上 |
| 一句话识别 | **5000次** | 同上 |

超额后按量计费，单价约 1.4元/小时（USD $1.4/h 国际站，国内站价格需在官网确认）。

### Whisper 自建 ASR 在轻量服务器上的可行性

| 模型 | 模型大小 | 内存占用 | CPU 1核速度 | 1核1G可行？ |
|:----|:-------:|:--------:|:----------:|:-----------:|
| Whisper-Tiny | ~75MB | ~390MB | ~3×实时 | ⚠️ 勉强可行（OS~500MB + Whisper~390MB ≈ 仅剩~100MB） |
| Whisper-Base | ~150MB | ~700MB | ~2×实时 | ❌ 不够 |
| Whisper-Small | ~500MB | ~1.5GB | ~实时 | ❌ 不够 |

**结论**：1核1G 只能跑 Whisper-Tiny，且几乎没有内存余量给其他服务。推荐 **1核2G 起步** 或直接用腾讯云 ASR 免费额度（前10小时免费）。

### 自建 Immich + COS 成本估算

Immich（自托管 Google Photos 替代）部署在 HK Lighthouse：

| 组件 | 月费 | 说明 |
|:----|:----:|:-----|
| HK Lighthouse 1核2G | ~34元 | 跑 Immich 服务器 + ML（CLIP + 人脸识别） |
| COS 标准存储（~20GB/月） | ~2.7元 | 20GB × 0.136元/GB |
| **合计** | **~37元/月** | 纯照片上云方案 |

⚠️ **Immich + Hermes Agent 同机不建议 1核**：Immich ML 服务（microservices）需要额外内存。同机推荐 2核2G（67元/月）或分开两台 1核1G（48元/月）。
