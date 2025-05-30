#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
پنجره اصلی برنامه
"""

import tkinter as tk
from tkinter import ttk
import logging

from .tabs import MainTab, ReportTab, ChartTab, AITab, ReminderTab, UserSettingsTab
from .utils import create_persian_style, show_message

logger = logging.getLogger(__name__)

class MainWindow:
    def __init__(self, app):
        """مقداردهی اولیه پنجره اصلی"""
        self.app = app
        self.config = app.config
        
        # ایجاد پنجره اصلی
        self.root = tk.Tk()
        self.root.title("سیستم مدیریت قند خون")
        self.root.geometry(self.config['UI']['window_size'])
        
        # تنظیم استایل فارسی
        self.style = create_persian_style(self.root)
        
        # ایجاد نوار منو
        self._create_menu()
        
        # ایجاد نوار وضعیت
        self._create_status_bar()
        
        # ایجاد تب‌ها
        self._create_tabs()
        
        logger.info("پنجره اصلی ایجاد شد")
        
    def _create_menu(self):
        """ایجاد نوار منو"""
        menubar = tk.Menu(self.root)
        
        # منوی فایل
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="خروج", command=self.root.quit)
        menubar.add_cascade(label="فایل", menu=file_menu)
        
        # منوی تنظیمات
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="تنظیمات کاربر", command=self._show_user_settings)
        menubar.add_cascade(label="تنظیمات", menu=settings_menu)
        
        # منوی راهنما
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="درباره", command=self._show_about)
        menubar.add_cascade(label="راهنما", menu=help_menu)
        
        self.root.config(menu=menubar)
        
    def _create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = ttk.Label(
            self.root,
            text="آماده",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def _create_tabs(self):
        """ایجاد تب‌ها"""
        self.notebook = ttk.Notebook(self.root)
        
        # تب اصلی
        self.main_tab = MainTab(
            self.notebook,
            self.app.db_manager,
            self.config,
            self.config['UI']['colors'],
            self.config['UI']['fonts']
        )
        self.notebook.add(self.main_tab, text="ثبت قند خون")
        
        # تب گزارش‌ها
        self.report_tab = ReportTab(
            self.notebook,
            self.app.db_manager,
            self.config,
            self.config['UI']['colors'],
            self.config['UI']['fonts']
        )
        self.notebook.add(self.report_tab, text="گزارش‌ها")
        
        # تب نمودارها
        self.chart_tab = ChartTab(
            self.notebook,
            self.app.db_manager,
            self.config,
            self.config['UI']['colors'],
            self.config['UI']['fonts']
        )
        self.notebook.add(self.chart_tab, text="نمودارها")
        
        # تب هوش مصنوعی
        self.ai_tab = AITab(
            self.notebook,
            self.app.db_manager,
            self.app.ai_analyzer,
            self.config,
            self.config['UI']['colors'],
            self.config['UI']['fonts']
        )
        self.notebook.add(self.ai_tab, text="هوش مصنوعی")
        
        # تب یادآوری‌ها
        self.reminder_tab = ReminderTab(
            self.notebook,
            self.app.db_manager,
            self.config,
            self.config['UI']['colors'],
            self.config['UI']['fonts']
        )
        self.notebook.add(self.reminder_tab, text="یادآوری‌ها")
        
        # تب تنظیمات کاربر
        self.settings_tab = UserSettingsTab(
            self.notebook,
            self.app.db_manager,
            self.config,
            self.config['UI']['colors'],
            self.config['UI']['fonts']
        )
        self.notebook.add(self.settings_tab, text="تنظیمات")
        
        self.notebook.pack(expand=True, fill=tk.BOTH)
        
    def _show_user_settings(self):
        """نمایش تنظیمات کاربر"""
        self.notebook.select(self.settings_tab)
        
    def _show_about(self):
        """نمایش اطلاعات برنامه"""
        show_message(
            self.root,
            "درباره برنامه",
            "سیستم مدیریت قند خون\nنسخه 2.0\n\nتوسعه‌دهنده: تیم توسعه"
        )
        
    def update_status(self, message):
        """به‌روزرسانی نوار وضعیت"""
        self.status_bar.config(text=message)
        
    def run(self):
        """اجرای پنجره اصلی"""
        self.root.mainloop()