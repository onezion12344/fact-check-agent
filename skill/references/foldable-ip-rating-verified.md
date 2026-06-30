# 折疊屏防水等級核查筆記（2026.06.26 session）

## IP 代碼速查

```
IP  5   8
    ↑   ↑
   防塵  防水

IP5_ = 有限防塵（灰塵可少量進入，不影響運作）
IP6_ = 完全防塵（無塵進入）
X    = 該項無測試/不認證

_8 = 浸水 1.5m / 30 分鐘
_9 = 高壓熱水噴射（80°C, 100 bar, 10-15cm）
```

## 各機型防水等級（已驗證）

| 機型 | 等級 | 來源 | 資料日期 |
|:-----|:-----|:-----|:---------|
| 三星 Z Fold 3 | **IPX8** | Samsung 官網、Counterpoint Research | 2021 |
| 三星 Z Fold 6 | **IP48** | Samsung 官網、Android Central | 2024 |
| 三星 Z Fold 7 | **IP48** | 延續前代 | 2025 |
| OPPO Find N5 | **IPX6/IPX8/IPX9** | OPPO 官網 ("world's first foldable with triple IP") | 2025 |
| **OPPO Find N6** | **IP58/IP59** | GSMArena（1m / 30min 浸水 + 高壓熱水） | 2026 |
| vivo X Fold 6 | **IP58/IP59** | Android Authority | 2026 |
| OnePlus Open | **IPX4** | GSMArena | 2023 |
| 榮耀 Magic V6 | **IP68/IP69** | 廠商宣稱 | 2026 |

## 核查重點

### 1. IP58 ≠ IP68

- IP5_ = 有限防塵（灰塵可少量進入）
- IP6_ = 完全防塵
- 折疊屏因鉸鏈有縫，多數只能做到 IP5_（有限防塵），極少數做到 IP68（完全防塵）
- **OPPO Find N6 標的是 IP58/IP59，不是 IP68**——GSMArena 已確認

### 2. X 的含義

X = 該項沒做測試/不認證。不代表做唔到，只係官方唔 guarantee。
- IPX8 = 防水 8 級有測，防塵冇測
- IPX4 = 防水 4 級有測，防塵冇測

### 3. 可靠信息來源優先級

| 優先級 | 來源 | 例子 |
|:-------|:-----|:-----|
| 🥇 | GSMArena 規格頁 | 最標準化，型號+等級一起列出 |
| 🥇 | 廠商官網 | OPPO.com, Samsung.com |
| 🥈 | 知名科技媒體 | Android Authority, Android Central, PhoneArena |
| ❌ | 電商平台 listing | 經常寫錯（把 IPX4 寫成 IP68）|
| ❌ | 自媒體/YouTube | 口誤常見 |
| ❌ | LLM 記憶 | 會編造數字（本 session 例子：我編了「20萬次摺疊仍密封」）|

### 4. 本 session 修正的錯誤

| 我說的 | 實際 | 修正 |
|:-------|:-----|:-----|
| vivo X Fold 6 防水 IPX8+IPX9 | **IP58 + IP59** | Android Authority 確認 |
| 三星用 Conformal Coating | **柔性有機矽密封膠 + 特殊潤滑脂 + 壓敏膠** | 三層不同手段，不是單一塗層 |
| 摺疊 20 萬次仍密封 | ❌ **無來源，虛構數字** | 三星只公佈 IPX8 測試通過，沒公佈摺疊次數下的防水耐久性 |
| 有「排水通道」設計 | ❌ **我猜的** | 三星沒提到排水通道 |

### 5. OnePlus Open USB-C DisplayPort 爭議

- **BestBuy 規格**：DisplayPort Over USB-C: None
- **GSMArena 規格**：USB Type-C 3.1, OTG（沒有 DisplayPort）
- **Reddit 用戶實測**：USB-C to HDMI 可鏡像螢幕（摺疊/展開都行）
- **結論**：能用 USB-C 出畫面，但非官方支援的 DisplayPort Alt Mode，不保證穩定。不要跟 DeX 比。
