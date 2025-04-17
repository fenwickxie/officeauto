#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project : officeauto
@File    : scheduler.py.py
@IDE     : PyCharm
@Author  : xie.fangyu
@Date    : 2025/3/31 下午1:58
"""

import threading
import time
from datetime import datetime

import keyboard
import pyautogui
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

IDLE = 0
RUNNING = 1
STATUS = {IDLE: "空闲中", RUNNING: "运行中"}


class WeChatScheduler(QObject):
    log_signal = pyqtSignal(str)  # 日志信号
    status_signal = pyqtSignal(int)  # 状态信号

    def __init__(self):
        super().__init__()
        self.scheduled_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.execute_send)
        self.is_running = False
        self.schedule_thread = None
        self.current_window = None
        self.preparation_time = 5.0  # 预估准备操作需要的时间(秒)
        self.onetime_schedule = False
        # 消息内容缓存
        self.target = ""
        self.content = ""
        self.shortcuts = {
            "open_wechat": "ctrl+alt+w",
            "open_search": "alt+f",
            "send_message": "ctrl+enter",
        }


    def update_shortcuts(self, shortcuts):
        """更新快捷键设置"""
        self.shortcuts.update(shortcuts)
        self.log_signal.emit(f"快捷键已更新: {self.shortcuts}")

    def start_once_schedule(self, target, content, scheduled_time):
        """启动一次性定时任务"""
        self.onetime_schedule = True  # 设置一次性任务标志
        if not self.validate_inputs(target, content, scheduled_time):
            return

        self.target = target
        self.content = content
        self.scheduled_time = scheduled_time

        self.is_running = True
        self.status_signal.emit(RUNNING)
        self.log_signal.emit("启动一次性定时任务")

        now = datetime.now()
        total_delay = (self.scheduled_time - now).total_seconds()

        if total_delay > self.preparation_time:
            # 提前准备消息
            prep_time = total_delay - self.preparation_time
            self.status_signal.emit(RUNNING)
            self.log_signal.emit(f"将在 {prep_time:.1f} 秒后开始准备消息")
            threading.Timer(prep_time, self.prepare_for_send).start()
        else:
            # 时间太紧，立即准备
            self.log_signal.emit("时间紧张，立即开始准备消息")
            self.prepare_for_send()

    def start_repeating_schedule(self, target, content, days, send_time, is_weekly):
        """启动循环定时任务"""
        self.onetime_schedule = False  # 设置非一次性任务
        if not self.validate_repeat_inputs(target, content, days, is_weekly):
            return

        self.target = target
        self.content = content
        self.is_running = True
        self.status_signal.emit(RUNNING)
        self.log_signal.emit("启动循环定时任务")

        self.schedule_thread = threading.Thread(
            target=self.run_repeating_schedule, args=(days, send_time, is_weekly)
        )
        self.schedule_thread.daemon = True
        self.schedule_thread.start()

    def run_repeating_schedule(self, days, send_time, is_weekly):
        """循环定时任务线程"""
        self.log_signal.emit("循环定时任务线程已启动")
        while self.is_running:
            now = datetime.now()

            if is_weekly:
                # 检查是否是选定的星期几
                weekday = now.weekday()
                if weekday not in days:
                    time.sleep(1)
                    continue
            else:
                # 检查是否是选定的日期
                if now.day not in days:
                    time.sleep(1)
                    continue

            # 检查时间是否匹配
            target_datetime = datetime.combine(now.date(), send_time)

            if now >= target_datetime:
                # 今天的时间已过，等待明天
                time.sleep(1)
                continue

            # 计算等待时间
            wait_seconds = (target_datetime - now).total_seconds()

            if wait_seconds > self.preparation_time:
                # 提前准备
                self.log_signal.emit(
                    f"等待 {wait_seconds - self.preparation_time:.1f} 秒后开始准备 {target_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')} 的消息"
                )
                time.sleep(wait_seconds - self.preparation_time)
                if not self.is_running:
                    break

                self.status_signal.emit(RUNNING)
                self.log_signal.emit(
                    f"开始准备 {target_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')} 的消息"
                )

                if self.prepare_message():
                    # 计算剩余时间
                    remaining = (
                        target_datetime - datetime.now()
                    ).total_seconds() * 1000
                    if remaining > 0:
                        self.status_signal.emit(RUNNING)
                        self.log_signal.emit(
                            f"消息准备完成，等待 {remaining:.0f} 毫秒后发送"
                        )
                        self.timer.start(remaining)
                    else:
                        self.log_signal.emit("立即发送消息（准备时间过长）")
                        self.execute_send()
            else:
                # 时间不足，直接准备并发送
                self.log_signal.emit("时间紧张，立即准备并发送消息")
                if self.prepare_message() and self.is_running:
                    self.execute_send()

            # 发送后等待一段时间再检查，避免重复发送
            time.sleep(1)
        self.log_signal.emit("循环定时任务线程已退出")

    def stop_scheduler(self):
        """停止所有定时任务"""
        self.is_running = False
        self.timer.stop()
        if self.schedule_thread and self.schedule_thread.is_alive():
            self.schedule_thread.join()

        self.status_signal.emit(IDLE)
        self.log_signal.emit("定时任务已停止")

        # 尝试恢复窗口状态
        self.activate_previous_window()

    def send_message_now(self, target, content):
        """立即发送消息，不影响定时任务运行状态"""
        if not target or not content:
            self.log_signal.emit("错误: 目标或内容为空")
            return

        # 不改变运行状态，只执行发送流程
        original_target = self.target
        original_content = self.content

        self.target = target
        self.content = content

        self.status_signal.emit(RUNNING)
        self.log_signal.emit("开始立即发送流程...")
        if self.prepare_message():
            time.sleep(0.1)  # 确保准备完成
            self.execute_send()

        # 恢复原来的消息内容
        self.target = original_target
        self.content = original_content

        # 不改变定时任务运行状态
        if self.is_running:
            self.status_signal.emit(RUNNING)
        else:
            self.status_signal.emit(IDLE)

    def prepare_for_send(self):
        """准备发送并启动精准定时"""
        if not self.is_running:
            return

        self.status_signal.emit(RUNNING)
        self.log_signal.emit("开始准备消息...")
        if self.prepare_message():
            # 计算剩余时间
            # datetime.now() 返回的时间精度可以达到微秒级别（microseconds），而不是仅仅到毫秒级别（milliseconds）
            remaining = int((self.scheduled_time - datetime.now()).total_seconds() * 1000)
            if remaining > 0:
                self.status_signal.emit(RUNNING)
                self.log_signal.emit(f"消息准备完成，等待 {remaining:.0f} 毫秒后发送")
                self.timer.start(remaining)
            else:
                self.log_signal.emit("立即发送消息（准备时间过长）")
                self.execute_send()

    def prepare_message(self):
        """预先打开聊天窗口并输入消息内容，只差发送"""
        try:
            # 保存当前活动窗口以便后续恢复
            self.current_window = pyautogui.getActiveWindow()
            self.log_signal.emit("保存当前窗口状态")

            # 打开企业微信
            self.log_signal.emit(f"模拟按下 {self.shortcuts['open_wechat']} 打开企业微信")
            keyboard.press_and_release(self.shortcuts["open_wechat"])
            time.sleep(0.8)  # 等待搜索框出现
            # 按下Alt+F打开搜索框
            self.log_signal.emit(f"模拟按下 {self.shortcuts['open_search']} 打开搜索框")
            keyboard.press_and_release(self.shortcuts["open_search"])
            time.sleep(0.8)  # 等待搜索框出现

            # 输入目标对话名称
            self.log_signal.emit(f"输入目标对话: {self.target}")
            keyboard.write(self.target)
            time.sleep(1)  # 等待搜索结果

            # 按Enter选择第一个结果
            self.log_signal.emit("模拟按下 Enter 选择对话")
            keyboard.press_and_release("enter")
            time.sleep(1)  # 等待对话打开

            # 输入消息内容并保持分段
            self.log_signal.emit("开始输入消息内容")
            for line in self.content.split("\n"):
                keyboard.write(line)
                # Shift+Enter换行
                keyboard.press_and_release("shift+enter")
                time.sleep(0.1)

            # 删除最后一个多余的换行
            keyboard.press_and_release("backspace")
            time.sleep(0.1)

            self.log_signal.emit("消息准备完成，等待发送时机")
            return True

        except Exception as e:
            error_msg = f"准备消息出错: {str(e)}"
            self.log_signal.emit(error_msg)
            self.activate_previous_window()
            return False

    def execute_send(self):
        """在精确时间执行发送操作"""
        SEND_SUCCESS = True
        try:
            self.log_signal.emit("正在执行发送操作...")
            self.log_signal.emit(f"模拟按下 {self.shortcuts['send_message']} 发送消息")
            keyboard.press_and_release(self.shortcuts["send_message"])
            send_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            status_msg = f"消息已于 ({send_time}发送)"
            time.sleep(0.5)

            self.log_signal.emit(status_msg)

        except Exception as e:
            error_msg = f"发送出错: {str(e)}"

            self.log_signal.emit(error_msg)
            SEND_SUCCESS = False
        # 如果是一次性任务，停止调度器并更新状态
        if self.onetime_schedule:
            self.is_running = False
            self.status_signal.emit(IDLE)
        # 恢复之前的活动窗口
        self.activate_previous_window()
        return SEND_SUCCESS

    def activate_previous_window(self):
        """恢复之前的活动窗口"""
        if hasattr(self, "current_window") and self.current_window:
            try:
                self.log_signal.emit("恢复之前的窗口状态")
                self.current_window.activate()
            except Exception as e:
                self.log_signal.emit(f"恢复窗口失败: {str(e)}")

    def validate_inputs(self, target, content, scheduled_time):
        """验证一次性任务的输入"""
        if not target:
            self.log_signal.emit("错误: 请输入目标对话名称")
            return False

        if not content:
            self.log_signal.emit("错误: 请输入发送内容")
            return False

        if scheduled_time <= datetime.now():
            self.log_signal.emit("错误: 请选择未来的时间")
            return False

        return True

    def validate_repeat_inputs(self, target, content, days, is_weekly):
        """验证循环任务的输入"""
        if not target:
            self.log_signal.emit("错误: 请输入目标对话名称")
            return False

        if not content:
            self.log_signal.emit("错误: 请输入发送内容")
            return False

        if not days:
            msg = (
                "错误: 请至少选择一个工作日"
                if is_weekly
                else "错误: 请输入每月发送的日期"
            )
            self.log_signal.emit(msg)
            return False

        return True
