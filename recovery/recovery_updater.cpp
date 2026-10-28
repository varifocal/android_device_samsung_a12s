/*
 * Copyright (C) 2021-2025, The LineageOS Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
#include <android-base/properties.h>
#include "edify/expr.h"
#include "otautil/error_code.h"

// a12s: verify the bootloader binary version before the OTA writes dtbo.img.
//
// Samsung bootloader version string, e.g. "A127FXXSDDXJ5" (from
// androidboot.bootloader on the reference device; matches
// ro.*.build.version.incremental=A127FXXSDDXJ5 in the stock dump).
// Layout: model (0-4) + SW region id (5-7) + BL BINARY VERSION LETTER at
// index 8 (the 9th character) + revision (9-12). Letters advance per
// bootloader generation: the a21s (Android 12 vendor) required 'C'; stock
// a12s ships 'D' (A127FXXSDDXJ5). Require 'D' or newer.
// TODO: sec_debug.bin is absent from ~/rom/dump, so the historical minimum
// for unopened Android 11 units is unverified; 'D' is the verified stock value.
static constexpr char kMinBootloaderBinaryVersion = 'D';

Value* VerifyBootloader(const char* name, State* state,
                        const std::vector<std::unique_ptr<Expr>>& /*argv*/) {
  std::string bootloader = android::base::GetProperty("ro.boot.bootloader", "");
  if (bootloader.empty()) {
    return ErrorAbort(state, kFileGetPropFailure,
                      "%s() failed to read current bootloader version", name);
  }

  if (bootloader.length() < 9) {
    return ErrorAbort(state, kArgsParsingFailure,
                      "%s() bootloader string too short: %s", name, bootloader.c_str());
  }

  char ninth_char = bootloader[8]; // index 8 = 9th character = BL binary version
  if (ninth_char >= kMinBootloaderBinaryVersion && ninth_char <= 'Z') {
    return StringValue("1");
  } else {
    return StringValue("0");
  }
}

void Register_librecovery_updater_exynos850() {
  RegisterFunction("exynos850.verify_bootloader_min", VerifyBootloader);
}
