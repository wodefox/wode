import tkinter as tk
import random

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

# 显示终端界面
def show_terminal():
    # 创建一个新的Tkinter窗口
    terminal_root = tk.Tk()
    terminal_root.title("FteAPT单兵作战工具 v0.1")
    terminal_root.geometry("800x600")  # 设置窗口大小
    
    # 设置全局样式
    style_bg = "#1e1e1e"
    style_fg = "#bfbfbf"
    prompt_color = "#ffcc00"
    
    # 创建一个Frame来包含Text小部件和Scrollbar
    frame = tk.Frame(terminal_root, bg=style_bg)
    frame.pack(expand=True, fill="both")
    
    # 创建一个Text小部件来模拟终端
    terminal_text = tk.Text(frame, bg=style_bg, fg=style_fg, insertbackground="#ffffff", font=("Monaco", 12), wrap='word', borderwidth=0, highlightthickness=0)
    terminal_text.pack(side=tk.TOP, expand=True, fill="both")
    
    # 启用滚动条
    scrollbar = tk.Scrollbar(frame, command=terminal_text.yview, bg=style_bg, troughcolor=style_bg, activebackground=prompt_color)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    terminal_text.config(yscrollcommand=scrollbar.set)
    
    # 插入欢迎信息
    terminal_text.insert(tk.END, "Foxes的玩具集\n")
    terminal_text.tag_configure("prompt", foreground=prompt_color)
    terminal_text.insert(tk.END, "┌──(fox㉿foxes)-[~]\n└─$", "prompt")
    terminal_text.mark_set("input_start", "end-2c")
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
        
        # Insert the next prompt
        terminal_text.insert(tk.END, "┌──(fox㉿foxes)-[~]\n└─$", "prompt")
        terminal_text.mark_set("input_start", "end-2c")
        
        # Scroll to the end
        terminal_text.see(tk.END)
    
    # Bind key press events
    terminal_text.bind("<Key>", on_key_press)
    
    # Set focus to the Text widget
    terminal_text.focus_set()
    
    # Run the main loop
    terminal_root.mainloop()

# 创建全屏窗口来显示字符艺术
root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(bg=random_color())

# 创建一个Label来显示字符艺术
label = tk.Label(root, text=character_art, font=("Monaco", 14), bg=root.cget('bg'), fg=random_color())
label.pack(expand=True)

# 等待3秒后开始淡化字符艺术
root.after(3000, fade_text, label, 0)

# 运行主循环
root.mainloop()






