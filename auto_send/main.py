#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : officeauto 
@File    : main.py
@IDE     : PyCharm 
@Author  : xie.fangyu
@Date    : 2025/3/31 下午1:58 
"""

import sys
from PyQt5.QtWidgets import QApplication
from gui import WeChatSchedulerUI
from scheduler import WeChatScheduler

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        
        # 创建业务逻辑层实例
        scheduler = WeChatScheduler()
        
        # 创建UI层实例并注入业务逻辑
        window = WeChatSchedulerUI(scheduler)
        window.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        sys.exit(f"Error: {e}")

