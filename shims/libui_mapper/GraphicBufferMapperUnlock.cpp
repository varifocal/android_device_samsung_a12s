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

#include <android-base/unique_fd.h>

// Minimal stand-ins so we never pull in libui's full headers: the mangled
// name only depends on the underlying struct name of the parameter.
struct native_handle;

namespace android {

typedef int32_t status_t;
typedef struct native_handle native_handle_t;

// Re-declaration of just the two unlock() overloads. Member functions are
// not virtual and access no members, so this is layout-safe; the 2-arg
// declaration resolves against the real symbol exported by libui.
class GraphicBufferMapper {
  public:
    status_t unlock(const native_handle_t* handle);
    status_t unlock(const native_handle_t* handle, base::unique_fd* outFence);
};

// Old one-argument form imported by libexynoscamera3.so. The modern API
// moved the sync fence out as a parameter; we drop the fence on the floor
// (closing it marks it signaled), which is what the old callers expected.
status_t GraphicBufferMapper::unlock(const native_handle_t* handle) {
    base::unique_fd fence;
    return unlock(handle, &fence);
}

}  // namespace android
