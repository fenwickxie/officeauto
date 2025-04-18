#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025 4月 16 22:25
# @Author  : fenwickxie
# @PROJECT : officeauto
# @File    : build.py
# @Software: PyCharm

import PyInstaller.__main__
import platform

version = "1.1.0"  # 版本号

# 获取系统名称和架构
system_name = platform.system()  # 返回 'Windows', 'Linux', 'Darwin' 等
machine_arch = platform.machine()  # 返回 ''ARM', 'AMD64' 等

# 动态生成名称
app_name: str = f"auto_send_{system_name}_{machine_arch}_v{version}"

auto_send_build = [
    "auto_send/main.py",
    f"--name={app_name}",
    # "--onefile",  # 创建单文件捆绑的可执行文件
    "--onedir",  # 创建包含一个可执行文件的单文件夹捆绑包（默认值）
    "--windowed",
    "--icon=auto_send/icon.ico",
    "--hidden-import=PyQt5.QtCore",
    "--hidden-import=PyQt5.QtGui",
    "--hidden-import=PyQt5.QtWidgets",
    "--hidden-import=keyboard",
    "--hidden-import=pyautogui",
    "--distpath=auto_send/dist",
    "--workpath=auto_send/build",
    "--clean",
    "--log-level=WARN",
]
PyInstaller.__main__.run(auto_send_build)
