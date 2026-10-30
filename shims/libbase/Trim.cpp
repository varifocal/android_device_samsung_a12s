/*
 * Copyright (C) 2026 The LineageOS Project
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

#include <android-base/strings.h>

namespace android {
namespace base {

// Stock Android 13 libbase exported Trim as a plain
// std::string Trim(const std::string&) function. lineage-23.2 only exports
// template instantiations (_ZN7android4base4TrimI...EEES8_OT_...), so
// nfc_nci_nxpsn.so fails check_elf_file. Provide the old symbol by
// delegating to the exported template; no state, no layout, free function.
std::string Trim(const std::string& str) {
    return Trim<const std::string&>(str);
}

}  // namespace base
}  // namespace android
