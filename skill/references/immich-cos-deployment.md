# Immich + COS 自托管照片备份 — 部署参考

> 2026.06.26 更新。适用于在腾讯云香港 Lighthouse 部署 Immich，后端对接 COS 对象存储。
> 完整需求分析已存在用户 Notion 页面「📷 照片备份方案 — 腾讯云 COS + Root 策略」。

## 用户背景

- **设备**：OnePlus Ace 3 Pro（ColorOS CN），即将购入 OnePlus Open
- **需求**：照片自动备份到云端 → 本地只留压缩版/索引 → 原生相册正常用 → AI 智能搜索
- **优先级**：存储上云 #1（替换 OneDrive），不续费了

## 方案选择（Notion 已有完整调研）

| 方案 | 适合阶段 | 特点 | 成本 |
|:----|:--------|:-----|:----:|
| **Immich + COS** | 短期首选 | Flutter App，90k+⭐，CLIP 语义搜索，S3 原生支持 | ~37元/月 |
| Ente + COS | 备选 | 端到端加密，Flutter App，S3 原生支持 | ~37元/月 |
| 原生相册 + rclone sync | 长期（root 后） | 原生级流畅，Tasker 自动化 | ~3-10元/月（仅 COS） |

**推荐：短期 Immich，长期 root 后 Tasker + rclone（跟 Immich 共存作第二备份）**

## 部署要点

### 服务器选择

| 纯 Immich | 推荐配置 | 月费 | 
|:----------|:-------:|:----:|
| ✅ 够用 | 1核2G HK Lighthouse | **34元/月** |
| Immich + Hermes 同机 | 2核2G HK Lighthouse | **67元/月** |
| 分开两台 | 1核1G × 2 | **48元/月** |

### COS 配置

- **地域**：香港（COS 支持 S3 兼容 API）
- **Immich 环境变量**：`IMMICH_STORAGE_BACKEND=s3`
- **存储类型**：标准存储（0.136元/GB/月）
- **费用参考**：~20GB 照片 ≈ 2.7元/月

### 手机端

- **Immich App**（Flutter，Google Play / APK 均可装）
- **ColoOS CN 注意事项**：需管好后台权限，防止被系统杀进程
- **Root 后**：Immich 可转系统 app + Tasker + rclone 自动化

## 已知陷阱

- ❌ Immich 的 ML（人脸识别 / CLIP 搜索）比较吃内存，1GB 不够
- ❌ 1核1G 下 Whisper ASR 不可行（只剩~100MB 余量）
- ❌ FolderSync Pro 不原生支持 S3/COS
- ⚠️ COS 香港价格 ≠ 大陆价格（香港 0.136 vs 大陆 0.099~0.118 元/GB/月）
- ⚠️ 续费 24元 不可保证——买前检查「续费同价」标注

## 相关 Notion 页面

- 📷 `照片备份方案 — 腾讯云 COS + Root 策略`
- 🗂️ `存储上云 Plan — Priority #1`
- ☁️ `云服务方案调研`
