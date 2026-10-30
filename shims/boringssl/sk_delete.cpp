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

#include <openssl/stack.h>

// Samsung's Android 13 BoringSSL exported sk_delete(STACK*, size_t);
// 23.2's BoringSSL only exports OPENSSL_sk_delete() with identical
// semantics. C symbol, no C++ layout involved. On AArch64 the int vs
// size_t second-argument difference is harmless (w0 writes zero-extend).
extern "C" void* sk_delete(OPENSSL_STACK* st, size_t i) {
    return OPENSSL_sk_delete(st, i);
}
