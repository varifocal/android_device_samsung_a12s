# Samsung Galaxy A12 (a12s, SM-A127F/DS) device tree

Unofficial LineageOS 23.2 bring-up for the Exynos 850 Galaxy A12.
This tree is self-contained: it does not inherit `device/samsung/a21s-common`,
only *borrows* values from it (every borrowed value is commented inline in
`BoardConfig.mk` and was re-verified against stock `A127FXXSDDXJ5` evidence in
`~/rom/{dump,stock,logs}`).

## Status (end of Phase 2)

| check | result |
|---|---|
| `breakfast a12s` | **RC=0**, `TARGET_PRODUCT=lineage_a12s`, `TARGET_BUILD_VARIANT=userdebug`, `LINEAGE_VERSION=23.2-20261027-UNOFFICIAL-a12s` (`~/rom/logs/breakfast_a12s_final2.log`) |
| `m nothing` | **RC=0**, "build completed successfully" (`~/rom/logs/m_nothing_a12s_20.log`) |
| blobs | 342 in `vendor/samsung/a12s` (own git repo), all from the stock dump copy, never the phone |
| unresolved proprietary NEEDED | 0 (everything not in the vendor repo is provided by the source build — see `~/rom/logs/hal_compatibility_table.md`) |

No image has ever been built or flashed in Phase 2 (brief item 7: `m nothing`
only).

## Layout

| file | purpose |
|---|---|
| `BoardConfig.mk` | partition/kernel/VINTF/AVB/SELinux configuration, evidence comments per value |
| `lineage_a12s.mk` | product definition; also sets `TARGET_REQUIRES_HIDL_CAS_HAL := false` **before** the core product inherit (see below) |
| `device.mk` | packages, copies, overlays |
| `proprietary-files.txt` | 342 stock entries (categories copied from `a21s-common`) |
| `extract-files.py` | extraction entry point (blob fixups re-verified against A12 stock) |
| `vintf/` | stock device manifest (`target-level="5"`) + 29 stock fragments + stock device matrix |
| `prebuilt/` | stock `dtbo.img`, carved `recovery_dtbo.img` |
| `sepolicy/`, `overlay/`, `rro_overlays/`, `configs/`, `audio/`, `init/`, `recovery/`, `releasetools/`, `shims/`, `sku/`, `rro_overlays/` | supporting files |

## Deviations from `a21s-common` (all intentional, evidence inline)

1. **Filesystems**: stock A12 uses **ext4 for system/vendor/product/odm**
   (blkid on lpunpack'd images); a21s builds vendor/odm as erofs.
2. **Dynamic partitions**: stock `super` = 5679087616, group `group_basic` =
   5674893312, members `system vendor product odm` — **no `system_ext`**
   (stock fstab has no `/system_ext`, so `TARGET_COPY_OUT_SYSTEM_EXT` is not
   declared and `system_ext` is not in the partition list).
3. **AVB off** (`BOARD_AVB_ENABLE := false`) per brief Phase 2.3; stock fstab
   avb flags already dropped from the extracted fstab.
4. **SELinux permissive** for bring-up (`androidboot.selinux=permissive` in
   `BOARD_KERNEL_CMDLINE` + `SELINUX_IGNORE_NEVERALLOWS := true`). Stock
   cmdline is `enforce` — restoring enforce is a Phase 3+/4 item.
5. **Density 300 / 720×1600@60** (stock `ro.sf.lcd_density=300`, stock DTB
   panel fragment), a21s uses 280 for its own panel.
6. **DTBO prebuilt**: `BOARD_PREBUILT_DTBOIMAGE` + `BOARD_KERNEL_SEPARATED_DTBO := false`
   (see TODO-DTBO below), a21s builds dtbo from source with `:= true`.
7. **`TARGET_KERNEL_CONFIG := exynos850-a12snsxx_defconfig`** — this defconfig
   does **not exist yet**; the brief assigns its creation to Phase 3. Any
   target that actually builds the kernel will fail until then (`m nothing`
   does not reach it).
8. **Camera `extra_ids`**: a21s sets `samsungCameraVars extra_ids 52,54` for
   its depth/macro cameras; a12's camera IDs are not derivable from anything
   on disk → deliberately omitted (TODO-CAMERA).
9. **Cache size** `209715200` **verified on the phone**:
   `blockdev --getsize64 /dev/block/by-name/cache` = `209715200` (measured
   2026-10-28, same value a21s uses). Stock images still carry no cache
   evidence (all four dynamic partitions + userdata only).
10. **`VENDOR_SECURITY_PATCH := 2024-10-01`** (stock
    `ro.vendor.build.security_patch`), a21s uses 2024-05-01.

## Why `TARGET_REQUIRES_HIDL_CAS_HAL := false` lives in `lineage_a12s.mk`

`build/make/target/product/base_vendor.mk:98-101` adds
`android.hardware.cas@1.2-service` for shipping API ≤ 33. That block is parsed
when the *core* product is inherited, so setting the flag in `device.mk`
(here inherited at `lineage_a12s.mk:24`) is **too late and has no effect**.
Setting it in `lineage_a12s.mk` *before* the core inherits works, and is
verified: `get_build_var PRODUCT_PACKAGES_SHIPPING_API_LEVEL_33` no longer
lists it, `PRODUCT_PACKAGES` lists only
`android.hardware.cas@1.2-service-lazy_samsung`.

## TODOs (Phase 3+; none of these are silently hacked around)

| id | what | evidence / why it is open |
|---|---|---|
| **TODO-NFC** | NFC has two registrars: stock `nxp.android.hardware.nfc@1.2-service` (`proprietary-files.txt:95`, stock rc registers `INfc@1.0/1.1/1.2` **and** `vendor.samsung.hardware.nfc@2.0::ISehNfc`) *and* source `android.hardware.nfc-service.sec` (`device.mk:297`). | two modules would race for `android.hardware.nfc@1.2::INfc/default` at runtime; pick one and drop the other's vintf fragment |
| **TODO-CAMERA** | stock `vendor.samsung.hardware.camera.provider@4.0-service_64` (`pf:99`, its fragment declares `android.hardware.camera.provider@2.6::ICameraProvider/legacy/0`) *and* source `android.hardware.camera.provider-service.samsung` (`device.mk:85`). Also `samsungCameraVars extra_ids` omitted (no evidence). | same-instance race + unknown camera IDs |
| **TODO-THERMAL** | stock HIDL `vendor.samsung.hardware.thermal@1.0-service` (`pf:108`, fragment has `override="true"` for `android.hardware.thermal@1.0/@2.0`) *and* AIDL `android.hardware.thermal-service.pixel` (`device.mk:284`). | different VINTF formats → no build clash, but two thermal governors; decide which drives cooling |
| **TODO-SEH-AUDIO** | stock declares `vendor.samsung.hardware.audio@1.0::ISehDevicesFactory/default`, served on stock only by `vendor/bin/hw/android.hardware.audio.service` (`strings` → `ISehDevicesFactory`). That name collides with AOSP's module (`hardware/interfaces/audio/common/all-versions/default/service/Android.bp:39`, installed at `device.mk:44`), so the stock binary cannot be extracted as-is. | declared-but-unserved HAL; only `vendor/lib64/hw/vendor.samsung.hardware.audio@1.0-impl.so` (`pf:135`) is present |
| **TODO-BT-SEH** | stock declares `vendor.samsung.hardware.bluetooth@2.0::ISehBluetooth/default`, served on stock only by `vendor/bin/hw/android.hardware.bluetooth@1.0-service` (`strings` → `ISehBluetooth`), same-name collision with the AOSP module installed at `device.mk:76`. | declared-but-unserved; only the interface lib `pf:59` is extracted |
| **TODO-BT-AUDIO** | stock declares `vendor.samsung.hardware.bluetooth.audio::ISehBluetoothAudioProviderFactory/default`; stock's server is again `android.hardware.audio.service` (`strings` → `ISehBluetoothAudioProviderFactory`, `vendor.samsung.hardware.bluetooth.audio-impl`). `device.mk:45-46` build AOSP's `android.hardware.bluetooth.audio-impl` + `audio.bluetooth.default`, which register a *different* package. | declared-but-unserved Samsung BT-Audio provider factory |
| **TODO-POWER** | AIDL `android.hardware.power::IPower/default`: stock `android.hardware.power.samsung-service` (`pf:92`) *and* `android.hardware.power-service.pixel-libperfmgr` (`device.mk:250`). | two AIDL registrars, one instance |
| **TODO-VIBRATOR** | AIDL `IVibrator/default`: stock `vendor.samsung.hardware.vibrator-service` (`pf:112`) *and* `android.hardware.vibrator-service.samsung` (`device.mk:102`). | two AIDL registrars |
| **TODO-HEALTH** | AIDL `IHealth/default`: stock `vendor.samsung.hardware.health-service` (`pf:100`) *and* `android.hardware.health-service.samsung` (`device.mk:139`). | two AIDL registrars |
| **TODO-FINGERPRINT** | HIDL `IBiometricsFingerprint/default` (2.1): stock 3.0 service (`pf:98`, its fragment declares 2.1) *and* `android.hardware.biometrics.fingerprint-service.samsung` (`device.mk:98`). | two registrars for one HIDL instance |
| **TODO-WIFI** | HIDL `android.hardware.wifi@1.6::IWifi/default`: stock `android.hardware.wifi@1.0-service` (`pf:157`) *and* AIDL `android.hardware.wifi-service` (`device.mk:307`). | stock HIDL service starts with the class main while the framework will use AIDL → possible nl80211 contention |
| **TODO-COMPOSER** | HIDL composer 2.2 (`pf:91`) *and* AIDL `android.hardware.composer.hwc3-service.slsi` (`device.mk:106`). | framework prefers AIDL when its fragment is present; stock HIDL service would idle |
| **TODO-SEPOLICY** | `SELINUX_IGNORE_NEVERALLOWS := true` and permissive cmdline are bring-up only; `device/samsung/a12s/sepolicy/vendor` is minimal. | neverallow audit + enforcing still pending |
| **TODO-OVERLAY** | `DEVICE_PACKAGE_OVERLAYS` + `rro_overlays/` are carried over unverified against stock RROs (`~/rom/dump` has no complete RRO inventory yet). | needs a stock `overlay` dump pass |
| **TODO-DTBO** | `BOARD_KERNEL_SEPARATED_DTBO := false` is required because `vendor/lineage/build/tasks/kernel.mk:664` would otherwise generate `$(BOARD_PREBUILT_DTBOIMAGE)` *into the source tree* (kati: "writing to readonly directory"); `build/make/core/Makefile:1054` installs the prebuilt when false. Tension: the normal source-dtbo flow is disabled while the prebuilt stock dtbo is used. | Phase 3 must keep the source-built base DTB compatible with stock dtbo entries (r00 custom0/1 = 0/0, r01 = 1/0x20) |
| **TODO-KERNEL-DEFCONFIG** | `exynos850-a12snsxx_defconfig` is referenced but not created (Phase 3 task per brief). | any real kernel build fails until then |
| **rc-override warnings** | 3 `overriding commands` warnings in `m nothing` — `android.hardware.graphics.allocator@4.0-service.rc`, `android.hardware.graphics.composer@2.2-service.rc`, `dumpstate-default.rc` (stock rc wins over the source module's rc). | intended "stock rc wins" pattern; harmless for `m nothing`, but the source modules' rcs are ignored at runtime |
| **rc → binary audit** | all 53 extracted `vendor/etc/init/*.rc` files audited against the entry list; 16 dangling refs found and fixed (10 binaries + 7 libs extracted, `cbd`/`secril_config_svc` covered by source modules, commit `edce6ed`). 3 remain **because stock itself has them**: `vendor/bin/snap_utility_32`, `vendor/bin/vcd` (stock rc marks it `disabled`), `vendor/bin/wpal` — none exist anywhere in the stock dump (odm/product/system/system_root/vendor). We keep the stock rcs verbatim rather than editing them. | documented, stock-identical behaviour |
| **extract-utils patch** | `tools/extract-utils` branch `a12s-cc-prebuilt-overrides` commit `88ab3a2` (emit `overrides` for cc prebuilts from `;OVERRIDES=`) is **no longer used** by a12s proprietary-files (the cas entry now uses `;MODULE_SUFFIX=_samsung`). Kept locally, never pushed. | dead code in this tree — remove or keep for reuse in Phase 3 |
| **BUILD_BROKEN_* flags** | `BUILD_BROKEN_DUP_RULES` + `BUILD_BROKEN_ELF_PREBUILT_PRODUCT_COPY_FILES` were needed for duplicated prebuilt ELF blobs in the draft stage. | re-audit before any release build |

Full per-HAL coverage (E/L/DUAL/GAP) with citations:
`~/rom/logs/hal_compatibility_table.md` (61 stock VINTF entries).
