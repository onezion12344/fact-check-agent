# 摺疊屏防水與手寫筆事實 — 2026.06 驗證

## IP 等級速查

| 等級 | 防護 | 說明 |
|:-----|:-----|:------|
| IPX4 | 防濺水 | 任何方向潑水，10分鐘 |
| IP48 | 防 >1mm 物體 + 浸水 1.5m/30min | 三星 Z Fold 6/7 |
| IP58 | 有限防塵 + 浸水 1m/30min | OPPO Find N6、vivo X Fold 6 |
| IP59 | 有限防塵 + 高壓熱水噴射 | OPPO Find N6、vivo X Fold 6 |
| IPX8 | 浸水 1.5m/30min（防塵未測） | 多數摺疊屏 |
| IPX9 | 高壓熱水噴射（防塵未測） | OPPO Find N5 |
| IP68 | 完全防塵 + 浸水 | 僅直板機能達到 |

## X 的含義

**X = 該項未測試/未認證。** 唔代表做唔到，只係官方冇 guarantee。摺疊屏因為鉸鏈有縫，好難做到完全防塵（IP6_），所以多數摺疊屏標 IPX8 而非 IP68。來源：IEC 60529 標準。

## 防水技術演進

### 三星 Z Fold 3（2021）— 首個 IPX8 摺疊屏
- Counterpoint Research 確認為「world's first water resistant foldable smartphone」
- Samsung 用三層手段：鉸鏈專用潤滑脂（防鏽防腐蝕）、內部零件納米防水塗層、柔性螢幕壓敏膠密封
- 來源：Samsung 官方技術影片（2021.08）、Dow Chemical 案例研究、iFixit 拆解、CNET 水測試

### 注意：我之前錯誤地稱之為「Conformal Coating」— 實際三星用的是「flexible silicone sealant + 專用潤滑脂 + 壓敏膠」三層組合。Conformal Coating 通常指 PCB 上的保形塗層，三星的防水方案更複雜。來源校正：Sammyfans 2021.08、「Dow flexible silicone sealant」案例。

### 錯誤追認
- 「開合 20 萬次依然密封」— ❌ 無來源，自行編造
- 「排水通道設計」— ❌ 三星從未提及，自行推測
- 「邊緣密封膠在 2024-2025 才解決」— ❌ 無具體時間點來源

## 2026 年摺疊屏手寫筆支援（修正後）

| 品牌 | 型號 | 支援筆？ | 註 |
|:-----|:-----|:--------|:---|
| OPPO | Find N6 | ✅ OPPO AI Pen（另購） | 自 Find N2 起支援 |
| 榮耀 | Magic V6 | ✅ **Magic-Pen** 🔥 | 官方標明「為折疊螢幕校準書寫精度」。我此前錯誤地説榮耀冇筆 |
| 華為 | Mate X7 | ✅ M-Pencil | 華為生態已知 |
| OnePlus | Open | ✅ OPPO Pen 相容 | 用同一個 touch digitizer |
| Motorola | Razr Fold 2026 | ✅ 即將推出 | CES 2026 預覽 |
| 三星 | Z Fold 7 | ❌ **取消** | 三星官方稱為「trade-off」為了做薄 |
| vivo | X Fold 6 | ❌ | vivo 有推出平板用 Pencil2s/Pencil3，但 X Fold 6 不支援 |
| 小米 | MIX Fold 5 | ❌ | 未有相關支援 |

### 市場趨勢糾正

我之前説「大家都不用筆」— 正確嘅市場情況係：
- 三星 Z Fold 7 取消 S Pen 係為咗做薄，**唔係因為冇人用**（來源：TechRadar 引述三星產品總監）
- 三星取消後反而「其他廠商爭住加入」— OPPO、榮耀、Motorola 都在 2026 年 push 手寫筆（來源：9to5Google 2026.01）
- 關於「市場數據證實 pen 購買率低」— **我沒有任何來源支持呢個 claim**，不應在無數據下作此結論

### OPPO Pen 技術細節
- 52audio 拆解：OPPO Pen = Goodix GP850 主動電容筆，不依賴 EMR 數位板層
- OPPO 官方相容列表（opposhop.cn）：僅 Find N2/N3/N5/OnePlus Open
- 普通手機不支援—觸控控制器需固件支援 USI/HPP 筆協議
- 來源：Android Central 實測、Android Authority 確認、Reddit r/OnePlusOpen 用戶回報
