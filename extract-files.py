#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2025 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixup_vendorcompat,
    lib_fixups_user_type,
    libs_proto_3_9_1,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'device/samsung/a12s',
    'hardware/samsung',
    'hardware/samsung_slsi-linaro/exynos',
    'hardware/samsung_slsi-linaro/graphics',
    'hardware/samsung_slsi-linaro/exynos/gralloc/gralloc3',
]

def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None

lib_fixups: lib_fixups_user_type = {
    libs_proto_3_9_1: lib_fixup_vendorcompat,
    (
        # Stock blobs whose name also belongs to a rust source module
        # (external/rust/android-crates-io): the extracted cc prebuilt is
        # renamed _vendor so soong does not pair it with the rust crate
        # (pairing panics - libuuid - or has no vendor variant - libhyper).
        'libuuid',
        'libhyper',
    ) : lib_fixup_vendor_suffix
} # fmt: skip

# Blob fixups inherited from a21s-common: same SoC family (Exynos 850),
# but every fixup was re-verified against stock A127FXXSDDXJ5 - see the
# a21s-only note inside. extract-files fails loudly if a pattern does not
# match an a12s blob, which is the desired behaviour.
blob_fixups: blob_fixups_user_type = {
    'vendor/lib64/libsec-ril.so': blob_fixup()
	.sig_replace('80 0E 40 F9 E1 03 16 AA 82 0C 80 52 E3 03 15 AA',
            '80 0E 40 F9 E1 03 16 AA 82 0C 80 52 08 00 80 D2'),
    (
    'vendor/lib/libsensorlistener.so',
    'vendor/lib64/libsensorlistener.so',
    ) : blob_fixup()
        .add_needed('libshim_sensorndkbridge.so'),
    # a21s-only fixups deliberately NOT carried over for a12s (verified against
    # stock A127FXXSDDXJ5):
    #  - libcrypto-tm.so / libssl-tm.so: absent from the entire stock A12
    #    firmware (find over all four stock partitions), so the
    #    replace_needed('libssl.so','libssl-tm.so') fixup targets a file that
    #    does not exist here.
    #  - libkeymaster_helper.so / libskeymaster4device.so: stock A12 imports
    #    libcrypto.so directly (readelf -d), and every crypto symbol they
    #    import except ASN1_INTEGER_get_uint32 resolves in Lineage's system
    #    libcrypto (ASN1_INTEGER_get_uint32 is exported by
    #    vendor/lib64/libkeymaster_helper.so itself). a21s needs
    #    libcrypto-tm + libshim_crypto because its stock blobs differ; for a12s
    #    those replacements would create dependencies on files that do not
    #    exist. shims/libcrypto was removed accordingly.
    (
        'vendor/lib/sensors.grip.so',
        'vendor/lib64/sensors.grip.so',
        'vendor/lib/sensors.sensorhub.so',
        'vendor/lib64/sensors.sensorhub.so',
    ) : blob_fixup()
        .add_needed('libutils-v32.so')
        .binary_regex_replace(b'_ZN7android6Thread3runEPKcim', b'_ZN7utils326Thread3runEPKcim'),
    # Stock audio/BT HAL servers are installed at renamed paths
    # (vendor/bin/hw/*.samsung, PRODUCT_COPY_FILES in device.mk; the binaries
    # themselves are EXTRACT_ONLY so no soong module collides with the AOSP
    # source servers). Point the stock service lines at the renamed binaries.
    'vendor/etc/init/android.hardware.audio.service.rc': blob_fixup()
        .regex_replace(
            r'/vendor/bin/hw/android\.hardware\.audio\.service\n',
            '/vendor/bin/hw/android.hardware.audio.service.samsung\n',
        ),
    'vendor/etc/init/android.hardware.bluetooth@1.0-service.rc': blob_fixup()
        .regex_replace(
            r'/vendor/bin/hw/android\.hardware\.bluetooth@1\.0-service\n',
            '/vendor/bin/hw/android.hardware.bluetooth@1.0-service.samsung\n',
        )
        .regex_replace(
            r'[ \t]+interface vendor\.samsung[^\n]*\n',
            '',
        ),
    # host_init_verifier rejects HIDL `interface` lines that name an
    # interface with no hidl_interface target in the tree (no .hal sources):
    # all vendor.samsung.hardware.* / ISeh* packages. Stripping the
    # bookkeeping line keeps the service running (class hal / lazy start via
    # the kept AOSP interface lines is unaffected); the binaries still
    # register their Samsung interfaces with hwservicemanager at runtime.
    # AOSP interface lines (IBluetoothHci, INfc, ICameraProvider, ...) are
    # untouched. See ~/rom/logs/request.md for the full analysis.
    (
        'vendor/etc/init/nxp.android.hardware.nfc@1.2-service.rc',
        'vendor/etc/init/vendor.samsung.hardware.camera.provider@4.0-service_64.rc',
        'vendor/etc/init/vendor.samsung.hardware.hqm@1.0-service.rc',
        'vendor/etc/init/vendor.samsung.hardware.security.drk@2.0-service.rc',
        'vendor/etc/init/vendor.samsung.hardware.security.widevine.keyprov@1.0-service.rc',
        'vendor/etc/init/vendor.samsung.hardware.tlc.iccc@1.0-service.rc',
        'vendor/etc/init/vendor.samsung.hardware.tlc.kg@1.1-service.rc',
        'vendor/etc/init/vendor.samsung.hardware.tlc.ucm@2.0-service.rc',
        'vendor/etc/init/vendor.samsung.hardware.wifi@2.0-service.rc',
    ) : blob_fixup()
        .regex_replace(
            r'[ \t]+interface vendor\.samsung[^\n]*\n',
            '',
        ),
}  # fmt: skip

module = ExtractUtilsModule(
    'a12s',
    'samsung',
    namespace_imports=namespace_imports,
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
)

if __name__ == '__main__':
    utils = ExtractUtils.device(module)
    utils.run()
