# Root/Bootloader Status by Brand and OS Version

All data verified against XDA (2024-2026 threads), DroidWin, SammyGuru, The Verge, GitHub repos.

## Samsung
- One UI 8 (Android 16): OEM Unlock REMOVED. No workaround.
- Knox eFuse: Permanent hardware fuse, cannot be reset.
- KnoxPatch v0.8.2: Restores Secure Folder, Health, Wearable, Secure Wi-Fi, Private Share. NOT Pass/Wallet.
- Affected: Z Fold 7, Z Flip 7, S25 series

## OPPO (ColorOS)
- ColorOS 15 and earlier: Bootloader unlockable
- ColorOS 16.0.0.500+: PERMANENT BOOTLOADER LOCK (XDA Jan 2026)
- ColorOS 16.0.3.501+: ANTI-ROLLBACK FUSE (downgrade = hard brick)
- Deep Testing application required for ColorOS 16

## OnePlus (OxygenOS)
- OxygenOS 16: Bootloader unlock STILL PERMITTED (DroidWin Dec 2025)
- Application process added August 2025
- OnePlus Open CPH2551: Root guide on XDA (2023-2026)

## Magisk
- CLI: magisk -v, --list, --install-module, --denylist add, --sqlite
- Hiding: Magisk Alpha + Shamiko + Play Integrity Fix
- WeChat: Bypassable (Magisk Alpha + Shamiko + DenyList)
- Alipay: No known issues
