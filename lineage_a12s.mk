#
# Copyright (C) 2020-2025 The LineageOS Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# CAS HAL: stock Samsung ships only the lazy HIDL service
# (vendor/bin/hw/android.hardware.cas@1.2-service-lazy + its rc and vintf
# fragment, all extracted to vendor/samsung/a12s). base_vendor.mk:98-101
# installs the AOSP non-lazy android.hardware.cas@1.2-service for shipping
# API <= 33 unless this is false; that source module builds 32-bit only, and
# installing it next to stock's lazy service would double-declare
# android.hardware.cas@1.2::ICas/default (duplicate vintf fragment + two init
# services). Must be set before the core product inherits below (base_vendor.mk
# is parsed there), hence it lives here and not in device.mk.
TARGET_REQUIRES_HIDL_CAS_HAL := false

## Inherit from generic products, most specific first
$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/languages_full.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/non_ab_device.mk)

## Inherit from a12s device
$(call inherit-product, device/samsung/a12s/device.mk)

## Boot Animation (stock panel: 720 x 1600 @ 60 Hz, DTB fragment@lcd td4150)
TARGET_SCREEN_HEIGHT := 1600
TARGET_SCREEN_WIDTH := 720

## Inherit some common Lineage stuff
$(call inherit-product, vendor/lineage/config/common_full_phone.mk)

## Device identifier, this must come after all inclusions
PRODUCT_DEVICE := a12s
PRODUCT_NAME := lineage_a12s
PRODUCT_BRAND := samsung
PRODUCT_MODEL := SM-A127F
PRODUCT_MANUFACTURER := samsung

# Stock: ro.product.first_api_level=30 (vendor/build.prop)
PRODUCT_SHIPPING_API_LEVEL := 30

PRODUCT_GMS_CLIENTID_BASE := android-samsung
