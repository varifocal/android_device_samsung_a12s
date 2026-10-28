#!/bin/env python3
#
# Copyright (C) 2020-2024 The LineageOS Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import common
import re

def FullOTA_Assertions(info):
  OTA_Assertions(info)
  return

def FullOTA_InstallEnd(info):
  OTA_InstallEnd(info)
  return

def IncrementalOTA_Assertions(info):
  OTA_Assertions(info)
  return

def IncrementalOTA_InstallEnd(info):
  OTA_InstallEnd(info)
  return

def AddImage(info, basename, dest):
  name = basename
  data = info.input_zip.read("IMAGES/" + basename)
  common.ZipWriteStr(info.output_zip, name, data)
  info.script.AppendExtra('package_extract_file("%s", "%s");' % (name, dest))

def OTA_Assertions(info):
  # a12s: device/model asserts + bootloader minimum.
  # Bootloader version string: androidboot.bootloader=A127FXXSDDXJ5 on the
  # reference device (matches ro.*.build.version.incremental=A127FXXSDDXJ5 in
  # ~/rom/dump/odm.build.prop:19). Format: model(5) + SW id(3) + BL binary
  # version letter (index 8, the 9th char) + revision(4). Stock letter 'D'.
  # NOTE: ~/rom/dump/sec_debug.bin does NOT exist (verified 2026-10-28), so
  # 'D' is derived from the bootloader string alone; older units' letters are
  # unverified (TODO: confirm minimum on an unopened Android 11 unit).
  cmd = (
      'assert(getprop("ro.product.device") == "a12s" || '
      'abort("ERROR: This build is for the Galaxy A12 (a12s) only."););'
      'assert(getprop("ro.product.model") == "SM-A127F" || '
      'abort("ERROR: This build is for model SM-A127F only."););'
      'assert(exynos850.verify_bootloader_min("") == "1" || '
      'abort("ERROR: This build requires a bootloader with binary version D or newer (stock is A127FXXSDDXJ5). Please update your firmware."););'
  )
  info.script.AppendExtra(cmd)
  return

def PrintInfo(info, dest):
  info.script.Print("Patching {} image unconditionally...".format(dest.split('/')[-1]))

def OTA_InstallEnd(info):
  # a12s: BOARD_AVB_ENABLE=false for bring-up, so no vbmeta.img is built
  # (a21s flashed both dtbo and vbmeta here).
  PrintInfo(info, "/dev/block/by-name/dtbo")
  AddImage(info, "dtbo.img", "/dev/block/by-name/dtbo")
  return
