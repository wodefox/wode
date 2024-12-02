import tkinter as tk
import socket
import psutil
from threading import Thread
import time
import subprocess
from tkinter import filedialog, colorchooser
import ctypes
import sys
import json
import os
import random

# 配置文件路径
CONFIG_FILE_PATH = 'fteapt_config.json'

# 读取配置文件
def load_config():
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            return json.load(config_file)
    return {}

# 保存配置文件
def save_config(config):
    with open(CONFIG_FILE_PATH, 'w') as config_file:
        json.dump(config, config_file, indent=4)

# 获取内网IP地址
def get_local_ip():
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
        if local_ip == '127.0.0.1':
            # 如果获取到的是本地回环地址，尝试其他方法
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
    except Exception as e:
        local_ip = '无法获取内网IP'
    return local_ip

# 更新IP地址显示
def update_ip_addresses(terminal_root):
    local_ip = get_local_ip()
    ip_label.config(text=f"内网IP: {local_ip}")
    terminal_root.after(5000, lambda: update_ip_addresses(terminal_root))  # 每5秒更新一次

# 更新系统监控信息
def update_system_monitor():
    while True:
        memory_usage = psutil.virtual_memory().percent
        cpu_usage = psutil.cpu_percent(interval=1)
        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent / (1024 * 1024)  # 转换为MB
        bytes_recv = net_io.bytes_recv / (1024 * 1024)  # 转换为MB
        
        monitor_label.config(text=f"内存使用: {memory_usage}% | CPU使用: {cpu_usage}% | 网络发送: {bytes_sent:.2f} MB | 网络接收: {bytes_recv:.2f} MB")
        time.sleep(1)

# 处理终端命令
def handle_command(command):
    command = command.strip()
    output = ""
    
    if not command:
        return
    
    # 定义一些基本命令
    basic_commands = {
        "cls": clear_screen,
        "clear": clear_screen,
        "exit": exit_terminal
    }
    
    if command in basic_commands:
        basic_commands[command]()
        return
    
    output = f"未知命令: {command}"
    
    insert_output(output)

# 插入输出到终端
def insert_output(output):
    terminal_text.insert("end", output)
    terminal_text.insert(tk.END, "\n┌──(fox㉿foxes)-[~]\n└─$", "prompt")
    terminal_text.mark_set("input_start", "end-1c")
    terminal_text.see(tk.END)

# 清屏
def clear_screen():
    terminal_text.delete("1.0", tk.END)
    terminal_text.insert(tk.END, "欢迎使用作战工具 v0.1\n", font_bold)
    terminal_text.insert(tk.END, "┌──(fox㉿foxes)-[~]\n└─$", "prompt")
    terminal_text.mark_set("input_start", "end-1c")
    terminal_text.see(tk.END)

# 退出终端
def exit_terminal():
    terminal_root.quit()

# 更改主题
def change_theme(theme_name):
    global style_bg, style_fg, prompt_color, main_frame, left_toolbar_frame, top_toolbar_frame, terminal_frame, scrollbar, monitor_frame, ip_label, monitor_label, context_menu, buttons_left, buttons_top
    
    themes = {
        "dark": {"bg": "#2b2b2b", "fg": "#ffffff", "prompt": "#ffcc00"},
        "light": {"bg": "#ffffff", "fg": "#000000", "prompt": "#009900"},
        "solarized": {"bg": "#002b36", "fg": "#839496", "prompt": "#cb4b16"},
        "oceanic": {"bg": "#1b2b34", "fg": "#c5c8c6", "prompt": "#66d9ef"},
        "gruvbox_dark": {"bg": "#1d2021", "fg": "#ebdbb2", "prompt": "#fb4934"},
        "dracula": {"bg": "#282a36", "fg": "#f8f8f2", "prompt": "#ff79c6"},
        "monokai": {"bg": "#272822", "fg": "#f8f8f2", "prompt": "#e6db74"},
        "vscode": {"bg": "#1e1e1e", "fg": "#d4d4d4", "prompt": "#ce9178"},
        "zenburn": {"bg": "#3f3f3f", "fg": "#dcdccc", "prompt": "#dfaf8f"},
        "material": {"bg": "#263238", "fg": "#ffffff", "prompt": "#80cbc4"},
        "github": {"bg": "#ffffff", "fg": "#333333", "prompt": "#005cc5"},
        "ayu_mirage": {"bg": "#1f2430", "fg": "#d0d0d0", "prompt": "#ffac1f"},
        "base16_ocean": {"bg": "#2b303b", "fg": "#c0c5ce", "prompt": "#65737e"},
        "base16_material": {"bg": "#263238", "fg": "#eeffff", "prompt": "#80cbc4"},
        "base16_solarized_light": {"bg": "#fdf6e3", "fg": "#657b83", "prompt": "#dc322f"},
        "base16_gruvbox_hard": {"bg": "#1d2021", "fg": "#fabd2f", "prompt": "#cc241d"},
        "base16_github": {"bg": "#fafafa", "fg": "#333333", "prompt": "#005cc5"},
        "base16_atelier_lakeside": {"bg": "#161b1d", "fg": "#dfe3e6", "prompt": "#4ca864"},
        "base16_tomorrow_night_eighties": {"bg": "#2d2d2d", "fg": "#cccccc", "prompt": "#a6e22e"}
    }
    
    if theme_name in themes:
        new_colors = themes[theme_name]
        style_bg = new_colors["bg"]
        style_fg = new_colors["fg"]
        prompt_color = new_colors["prompt"]
        
        # 更新所有部件的颜色
        terminal_root.configure(bg=style_bg)
        main_frame.configure(bg=style_bg)
        left_toolbar_frame.configure(bg=style_bg)
        top_toolbar_frame.configure(bg=style_bg)
        terminal_frame.configure(bg=style_bg)
        terminal_text.configure(bg=style_bg, fg=style_fg, insertbackground=style_fg, highlightcolor=prompt_color)
        scrollbar.configure(bg=style_bg, troughcolor=style_bg, activebackground=prompt_color, width=15)
        monitor_frame.configure(bg=style_bg)
        ip_label.configure(bg=style_bg, fg=style_fg)
        monitor_label.configure(bg=style_bg, fg=style_fg)
        context_menu.configure(bg=style_bg, fg=style_fg)
        for button in buttons_left + buttons_top:
            button.configure(bg="#444444", fg=style_fg)
        
        terminal_text.tag_configure("prompt", foreground=prompt_color, font=font_normal)
        terminal_text.update_idletasks()

# 显示终端界面
def show_terminal():
    global terminal_root, ip_label, left_toolbar_frame, top_toolbar_frame, buttons_left, buttons_top, monitor_label, terminal_text, style_bg, style_fg, prompt_color, font_normal, font_bold, main_frame, terminal_frame, scrollbar, monitor_frame, context_menu
    
    terminal_root = tk.Tk()
    terminal_root.title("作战工具 v0.1")
    terminal_root.geometry("1000x600")  # 设置窗口大小
    
    # 加载配置
    config = load_config()
    theme_name = config.get('theme', 'dark')
    opacity = config.get('opacity', 1.0)
    
    # 设置全局样式
    style_bg = "#2b2b2b"
    style_fg = "#ffffff"
    prompt_color = "#ffcc00"
    
    # 设置字体
    font_normal = ("Arial", 12)
    font_bold = ("Arial", 12, "bold")
    
    # 弹出对话框以编辑主题
    def edit_theme_dialog():
        dialog = tk.Toplevel(terminal_root)
        dialog.title("编辑主题")
        dialog.geometry("300x400")
        
        theme_var = tk.StringVar(value=theme_name)
        
        # 创建一个框架来容纳滚动条和主题选项
        frame = tk.Frame(dialog, bg=style_bg)
        frame.pack(expand=True, fill="both")
        
        canvas = tk.Canvas(frame, bg=style_bg, borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview, bg=style_bg, troughcolor=style_bg, activebackground=prompt_color, width=15)
        scrollable_frame = tk.Frame(canvas, bg=style_bg)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 添加主题选项
        themes = [
            "dark", "light", "solarized", "oceanic", "gruvbox_dark", "dracula",
            "monokai", "vscode", "zenburn", "material", "github", "ayu_mirage",
            "base16_ocean", "base16_material", "base16_solarized_light", "base16_gruvbox_hard",
            "base16_github", "base16_atelier_lakeside", "base16_tomorrow_night_eighties"
        ]
        
        for theme in themes:
            radio_button = tk.Radiobutton(scrollable_frame, text=theme.capitalize(), variable=theme_var, value=theme, bg=style_bg, fg=style_fg, selectcolor=style_bg, font=font_normal)
            radio_button.pack(anchor="w", padx=10, pady=5)
        
        def apply_theme():
            selected_theme = theme_var.get()
            change_theme(selected_theme)
            config['theme'] = selected_theme
            save_config(config)
            dialog.destroy()
        
        apply_button = tk.Button(dialog, text="应用", bg="#444444", fg=style_fg, relief=tk.FLAT, bd=0, highlightthickness=0, command=apply_theme, font=font_normal)
        apply_button.pack(pady=10, padx=10, fill="x")
        
        # 绑定鼠标滚轮事件到Canvas
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    # 自定义颜色
    def set_custom_color():
        color_code = colorchooser.askcolor(title="选择颜色")[1]
        if color_code:
            change_theme(color_code)
    
    # 自定义透明度
    def set_custom_opacity():
        dialog = tk.Toplevel(terminal_root)
        dialog.title("自定义透明度")
        dialog.geometry("200x100")
        
        opacity_var = tk.DoubleVar(value=opacity)
        opacity_scale = tk.Scale(dialog, from_=0.0, to=1.0, resolution=0.01, orient=tk.HORIZONTAL, variable=opacity_var, label="透明度:", font=font_normal)
        opacity_scale.pack(pady=10, padx=10, fill="x")
        
        def apply_opacity():
            opac = opacity_var.get()
            terminal_root.attributes("-alpha", opac)
            config['opacity'] = opac
            save_config(config)
            dialog.destroy()
        
        apply_button = tk.Button(dialog, text="应用", bg="#444444", fg=style_fg, relief=tk.FLAT, bd=0, highlightthickness=0, command=apply_opacity, font=font_normal)
        apply_button.pack(pady=5, padx=10, fill="x")
    
    # 恢复默认
    def restore_default():
        terminal_root.attributes("-alpha", 1.0)  # 恢复不透明
        change_theme("dark")  # 恢复默认主题
        config['theme'] = 'dark'
        config['opacity'] = 1.0
        save_config(config)
    
    # 创建一个主框架来包含工具栏、终端区域和系统监控信息
    main_frame = tk.Frame(terminal_root, bg=style_bg)
    main_frame.pack(expand=True, fill="both")
    
    # 创建左侧工具栏框架
    left_toolbar_frame = tk.Frame(main_frame, bg=style_bg, width=100)
    left_toolbar_frame.pack(side=tk.LEFT, fill="y", padx=(10, 0), pady=10)
    
    # 创建顶部工具栏框架
    top_toolbar_frame = tk.Frame(main_frame, bg=style_bg, height=30)
    top_toolbar_frame.pack(side=tk.TOP, fill="x", padx=10, pady=(10, 0))
    
    # 初始化按钮列表
    buttons_left = []
    buttons_top = []
    
    # 添加一些示例按钮到左侧工具栏
    def add_tool_button(label, command=None, position="left"):
        if position == "left":
            frame = left_toolbar_frame
            list_to_append = buttons_left
        elif position == "top":
            frame = top_toolbar_frame
            list_to_append = buttons_top
        else:
            return
        
        button = tk.Button(frame, text=label, bg="#444444", fg=style_fg, relief=tk.FLAT, bd=0, highlightthickness=0, command=command, font=font_normal)
        button.pack(side=tk.TOP if position == "left" else tk.LEFT, padx=5, pady=5)
        
        # 绑定右键菜单到按钮
        button_menu = tk.Menu(button, tearoff=0, bg=style_bg, fg=style_fg)
        button_menu.add_command(label="删除", command=lambda btn=button: delete_selected_button(btn))
        button_menu.add_command(label="修改标签", command=lambda btn=button: edit_label_dialog(btn))
        button_menu.add_command(label="自定义启动位置", command=lambda btn=button: change_command_dialog(btn))
        button_menu.add_command(label="以管理员运行", command=lambda btn=button: run_as_admin(btn))
        
        def show_button_menu(event):
            button_menu.post(event.x_root, event.y_root)
        
        button.bind("<Button-3>", show_button_menu)
        
        list_to_append.append(button)
    
    # 弹出对话框以添加新按钮
    def add_new_button_dialog(position):
        dialog = tk.Toplevel(terminal_root)
        dialog.title("增加按钮")
        dialog.geometry("200x100")
        
        label_entry = tk.Entry(dialog, font=font_normal)
        label_entry.pack(pady=10, padx=10, fill="x")
        
        def add_button_from_dialog():
            label = label_entry.get().strip()
            if label:
                add_tool_button(label, lambda: print(f"{label} 被点击"), position)
                dialog.destroy()
        
        add_button = tk.Button(dialog, text="增加", bg="#444444", fg=style_fg, relief=tk.FLAT, bd=0, highlightthickness=0, command=add_button_from_dialog, font=font_normal)
        add_button.pack(pady=5, padx=10, fill="x")
    
    # 删除选中的按钮
    def delete_selected_button(button):
        if button in buttons_left:
            button.destroy()
            buttons_left.remove(button)
        elif button in buttons_top:
            button.destroy()
            buttons_top.remove(button)
    
    # 弹出对话框以修改按钮标签
    def edit_label_dialog(button):
        dialog = tk.Toplevel(terminal_root)
        dialog.title("修改标签")
        dialog.geometry("200x100")
        
        new_label_entry = tk.Entry(dialog, font=font_normal)
        new_label_entry.insert(0, button.cget('text'))
        new_label_entry.pack(pady=10, padx=10, fill="x")
        
        def edit_label_from_dialog():
            new_label = new_label_entry.get().strip()
            if new_label:
                button.config(text=new_label)
                dialog.destroy()
        
        edit_button = tk.Button(dialog, text="修改", bg="#444444", fg=style_fg, relief=tk.FLAT, bd=0, highlightthickness=0, command=edit_label_from_dialog, font=font_normal)
        edit_button.pack(pady=5, padx=10, fill="x")
    
    # 弹出对话框以更改按钮启动位置
    def change_command_dialog(button):
        dialog = tk.Toplevel(terminal_root)
        dialog.title("自定义启动位置")
        dialog.geometry("300x150")
        
        path_var = tk.StringVar(value="")
        path_entry = tk.Entry(dialog, textvariable=path_var, font=font_normal)
        path_entry.pack(pady=10, padx=10, fill="x")
        
        def browse_file():
            filepath = filedialog.askopenfilename(title="选择程序", filetypes=[("Executable files", "*.exe"), ("All files", "*.*")])
            if filepath:
                path_var.set(filepath)
        
        browse_button = tk.Button(dialog, text="浏览", bg="#444444", fg=style_fg, relief=tk.FLAT, bd=0, highlightthickness=0, command=browse_file, font=font_normal)
        browse_button.pack(pady=5, padx=10, side=tk.LEFT)
        
        def change_command_from_dialog():
            path = path_var.get().strip()
            if path:
                try:
                    # 尝试打开路径
                    def start_program():
                        try:
                            subprocess.Popen(path)
                        except PermissionError:
                            insert_output("权限不足，请以管理员身份运行此程序。")
                        except OSError as e:
                            insert_output(f"操作系统错误: {str(e)}")
                    
                    button.config(command=start_program)
                    button.path = path  # 存储路径到按钮对象
                    dialog.destroy()
                except Exception as e:
                    error_label.config(text=str(e), fg="red")
        
        change_button = tk.Button(dialog, text="设置", bg="#444444", fg=style_fg, relief=tk.FLAT, bd=0, highlightthickness=0, command=change_command_from_dialog, font=font_normal)
        change_button.pack(pady=5, padx=10, side=tk.RIGHT)
        
        error_label = tk.Label(dialog, text="", bg=style_bg, fg=style_fg, font=font_normal)
        error_label.pack(pady=5, padx=10, anchor="w")
    
    # 请求以管理员权限运行程序
    def run_as_admin(button):
        path = getattr(button, 'path', '').strip()
        if path:
            try:
                # 使用 ShellExecuteW 请求提升权限
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{sys.argv[0]}" "{path}"', None, 1)
            except Exception as e:
                insert_output(f"无法以管理员权限运行程序: {str(e)}")
        else:
            insert_output("请先设置启动位置。")
    
    # 创建终端框架
    terminal_frame = tk.Frame(main_frame, bg=style_bg)
    terminal_frame.pack(side=tk.TOP, expand=True, fill="both", padx=(0, 10), pady=(0, 10))
    
    # 创建一个Text小部件来模拟终端
    terminal_text = tk.Text(terminal_frame, bg=style_bg, fg=style_fg, insertbackground="#ffffff", font=font_normal, wrap='none', borderwidth=1, highlightthickness=1, highlightcolor=prompt_color)
    terminal_text.pack(side=tk.TOP, expand=True, fill="both")
    
    # 启用滚动条
    scrollbar = tk.Scrollbar(terminal_frame, command=terminal_text.yview, bg=style_bg, troughcolor=style_bg, activebackground=prompt_color, width=15)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    terminal_text.config(yscrollcommand=scrollbar.set)
    
    # 插入欢迎信息
    terminal_text.insert(tk.END, "欢迎使用作战工具 v0.1\n", font_bold)
    terminal_text.tag_configure("prompt", foreground=prompt_color, font=font_normal)
    terminal_text.insert(tk.END, "┌──(fox㉿foxes)-[~]\n└─$", "prompt")
    terminal_text.mark_set("input_start", "end-1c")
    terminal_text.see(tk.END)
    
    def on_key_press(event):
        if event.keysym == 'Return':
            handle_return()
            return 'break'
        elif event.keysym == 'BackSpace':
            # Allow backspace only if not at the start of the input
            if terminal_text.compare("insert", "<=", "input_start"):
                return 'break'
        return None
    
    def handle_return():
        # Get the user input from the Text widget
        user_input = terminal_text.get("input_start", "end-1c").strip()
        
        # Insert a newline after the input
        terminal_text.insert("end", "\n")
        
        # Handle the command
        handle_command(user_input)
        
        # Scroll to the end
        terminal_text.see(tk.END)
    
    # Create context menu
    context_menu = tk.Menu(terminal_text, tearoff=0, bg=style_bg, fg=style_fg)
    context_menu.add_command(label="复制", command=lambda: terminal_text.event_generate('<<Copy>>'))
    context_menu.add_command(label="剪切", command=lambda: terminal_text.event_generate('<<Cut>>'))
    context_menu.add_command(label="粘贴", command=lambda: terminal_text.event_generate('<<Paste>>'))
    context_menu.add_separator()
    context_menu.add_command(label="清屏", command=lambda: clear_screen(), font=font_normal)
    context_menu.add_command(label="编辑主题", command=edit_theme_dialog, font=font_normal)
    context_menu.add_command(label="自定义颜色", command=set_custom_color, font=font_normal)
    context_menu.add_command(label="自定义透明度", command=set_custom_opacity, font=font_normal)
    context_menu.add_command(label="恢复默认", command=restore_default, font=font_normal)
    
    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)
    
    # Bind right-click event to show context menu
    terminal_text.bind("<Button-3>", show_context_menu)
    
    # Bind key press events
    terminal_text.bind("<Key>", on_key_press)
    
    # Set focus to the Text widget
    terminal_text.focus_set()
    
    # 创建系统监控信息显示区域
    monitor_frame = tk.Frame(main_frame, bg=style_bg)
    monitor_frame.pack(side=tk.BOTTOM, fill="x", padx=10, pady=10)
    
    global ip_label, monitor_label
    ip_label = tk.Label(monitor_frame, text="内网IP: 正在获取...", bg=style_bg, fg=style_fg, font=font_normal)
    ip_label.pack(side=tk.LEFT, padx=10, pady=5, anchor="w")
    
    monitor_label = tk.Label(monitor_frame, text="内存使用: ...% | CPU使用: ...% | 网络发送: ... MB | 网络接收: ... MB", bg=style_bg, fg=style_fg, font=font_normal)
    monitor_label.pack(side=tk.LEFT, padx=10, pady=5, anchor="w")
    
    # 更新IP地址显示
    update_ip_addresses(terminal_root)
    
    # 启动系统监控线程
    monitor_thread = Thread(target=update_system_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # 应用加载的主题和透明度
    change_theme(theme_name)
    terminal_root.attributes("-alpha", opacity)
    
    # 添加一些示例按钮到工具栏
    add_tool_button("工具1", lambda: print("工具1被点击"), position="left")
    add_tool_button("工具2", lambda: print("工具2被点击"), position="left")
    add_tool_button("工具3", lambda: print("工具3被点击"), position="left")
    add_tool_button("工具A", lambda: print("工具A被点击"), position="top")
    add_tool_button("工具B", lambda: print("工具B被点击"), position="top")
    add_tool_button("工具C", lambda: print("工具C被点击"), position="top")
    
    # 左侧工具栏右键菜单
    left_toolbar_menu = tk.Menu(left_toolbar_frame, tearoff=0, bg=style_bg, fg=style_fg)
    left_toolbar_menu.add_command(label="增加按钮", command=lambda: add_new_button_dialog("left"))
    
    def show_left_toolbar_menu(event):
        left_toolbar_menu.post(event.x_root, event.y_root)
    
    left_toolbar_frame.bind("<Button-3>", show_left_toolbar_menu)
    
    # 顶部工具栏右键菜单
    top_toolbar_menu = tk.Menu(top_toolbar_frame, tearoff=0, bg=style_bg, fg=style_fg)
    top_toolbar_menu.add_command(label="增加按钮", command=lambda: add_new_button_dialog("top"))
    
    def show_top_toolbar_menu(event):
        top_toolbar_menu.post(event.x_root, event.y_root)
    
    top_toolbar_frame.bind("<Button-3>", show_top_toolbar_menu)
    
    # Run the main loop
    terminal_root.mainloop()

# 定义要显示的字符
character_art = """
███▄    █  ██▓  ▄████  ██░ ██ ▄▄▄█████▓     █████▒▒█████  ▒██   ██▒▓█████   ██████ 
██ ▀█   █ ▓██▒ ██▒ ▀█▒▓██░ ██▒▓  ██▒ ▓▒   ▓██   ▒▒██▒  ██▒▒▒ █ █ ▒░▓█   ▀ ▒██    ▒ 
▓██  ▀█ ██▒▒██▒▒██░▄▄▄░▒██▀▀██░▒ ▓██░ ▒░   ▒████ ░▒██░  ██▒░░  █   ░▒███   ░ ▓██▄   
▓██▒  ▐▌██▒░██░░▓█  ██▓░▓█ ░██ ░ ▓██▓ ░    ░▓█▒  ░▒██   ██░ ░ █ █ ▒ ▒▓█  ▄   ▒   ██▒
▒██░   ▓██░░██░░▒▓███▀▒░▓█▒░██▓  ▒██▒ ░    ░▒█░   ░ ████▓▒░▒██▒ ▒██▒░▒████▒▒██████▒▒
░ ▒░   ▒ ▒ ░▓   ░▒   ▒  ▒ ░░▒░▒  ▒ ░░       ▒ ░   ░ ▒░▒░▒░ ▒▒ ░ ░▓ ░░░ ▒░ ░▒ ▒▓▒ ▒ ░
░ ░░   ░ ▒░ ▒ ░  ░   ░  ▒ ░▒░ ░    ░        ░       ░ ▒ ▒░ ░░   ░▒ ░ ░ ░  ░░ ░▒  ░ ░
   ░   ░ ░  ▒ ░░ ░   ░  ░  ░░ ░  ░          ░ ░   ░ ░ ░ ▒   ░    ░     ░   ░  ░  ░  
         ░  ░        ░  ░  ░  ░                       ░ ░   ░    ░     ░  ░      ░
"""

# 生成随机RGB颜色
def random_color():
    return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

# 淡化字符的函数
def fade_text(label, fade_factor):
    assert 0 <= fade_factor <= 1, f"fade_factor must be between 0 and 1, got {fade_factor}"
    
    # 获取当前颜色
    current_fg = label.cget("fg")
    
    # 验证颜色是否为有效格式
    if not isinstance(current_fg, str) or not current_fg.startswith('#') or len(current_fg) != 7:
        print(f"Invalid color format: {current_fg}. Using default black.")
        current_fg = '#000000'
    
    r, g, b = tuple(int(current_fg[i:i+2], 16) for i in (1, 3, 5))
    
    # 计算新的颜色值
    new_r = int(r * (1 - fade_factor))
    new_g = int(g * (1 - fade_factor))
    new_b = int(b * (1 - fade_factor))
    
    # 设置标签的新前景颜色
    label.config(fg=f"#{new_r:02x}{new_g:02x}{new_b:02x}")
    
    if fade_factor < 1:
        root.after(50, fade_text, label, min(fade_factor + 0.05, 1))  # 递归调用以实现淡出效果
    else:
        root.destroy()  # 关闭全屏窗口
        show_terminal()

# 显示启动动画
def show_startup_animation():
    global root
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.overrideredirect(True)  # 去掉边框
    root.geometry(f"{screen_width}x{screen_height}+0+0")  # 全屏
    root.configure(bg=random_color())  # 初始背景色
    
    # 创建Label来显示字符艺术
    label = tk.Label(root, text=character_art, font=("Courier New", 20), justify="center", bg=root.cget("bg"), fg='#FFFFFF')
    label.pack(expand=True)
    
    # 淡化字符
    fade_text(label, 0)
    
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].endswith('.exe'):
        # If the script is called with an executable path, run it as admin
        path = sys.argv[1]
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", path, None, None, 1)
        except Exception as e:
            print(f"无法以管理员权限运行程序: {str(e)}")
    else:
        show_startup_animation()
