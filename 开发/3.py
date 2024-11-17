import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import json
import subprocess

# 获取用户主目录
USER_HOME = os.path.expanduser("~")

# 配置文件路径
CONFIG_DIR = os.path.join(USER_HOME, ".fteapt")
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "commands.json")

# 确保配置目录存在
if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

def load_commands():
    """Load custom commands from the configuration file."""
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, 'r') as file:
                commands = json.load(file)
                if isinstance(commands, dict):
                    return commands
                else:
                    raise ValueError("配置文件格式不正确")
        except (json.JSONDecodeError, ValueError) as e:
            messagebox.showerror("错误", f"加载配置文件时出错: {str(e)}")
            return {}
    else:
        default_commands = {}
        save_commands(default_commands)
        return default_commands

def save_commands(commands):
    """Save custom commands to the configuration file."""
    with open(CONFIG_FILE_PATH, 'w') as file:
        json.dump(commands, file)

class CommandModel:
    def __init__(self):
        self.commands = load_commands()

    def add_command(self, name, path, env, custom_env=None):
        if name in self.commands:
            messagebox.showwarning("警告", "该命令已存在")
            return False
        self.commands[name] = {'path': path, 'env': env, 'custom_env': custom_env}
        save_commands(self.commands)
        return True

    def delete_command(self, name):
        if name not in self.commands:
            messagebox.showwarning("警告", "该命令不存在")
            return False
        del self.commands[name]
        save_commands(self.commands)
        return True

    def modify_command(self, old_name, new_name, path, env, custom_env=None):
        if old_name not in self.commands:
            messagebox.showwarning("警告", "该命令不存在")
            return False
        if new_name != old_name and new_name in self.commands:
            messagebox.showwarning("警告", "该命令已存在")
            return False
        del self.commands[old_name]
        self.commands[new_name] = {'path': path, 'env': env, 'custom_env': custom_env}
        save_commands(self.commands)
        return True

    def get_commands(self):
        return self.commands

class TerminalView(tk.Tk):
    def __init__(self, controller=None):
        super().__init__()
        self.controller = controller
        self.title("FteAPT单兵作战工具 v0.3")
        self.geometry("800x600")
        
        # 设置全局样式
        style_bg = "#2b2b2b"
        style_fg = "#d4d4d4"
        prompt_color = "#9cdcfe"
        output_color = "#dcdcdc"
        error_color = "#f44747"
        
        self.style = ttk.Style()
        self.style.configure('.', background=style_bg, foreground=style_fg, font=("Consolas", 12))
        self.style.configure('TLabel', background=style_bg, foreground=style_fg, font=("Consolas", 12))
        self.style.configure('TEntry', fieldbackground=style_bg, foreground=style_fg, insertcolor="#ffffff", font=("Consolas", 12))
        self.style.configure('TButton', background=prompt_color, foreground=style_bg, font=("Consolas", 12))
        self.style.map('TButton', background=[('active', '#569cd6')])
        
        # 创建一个Frame来包含Text小部件和Scrollbar
        frame = ttk.Frame(self)
        frame.pack(expand=True, fill="both")
        
        # 创建一个Text小部件来模拟终端
        self.terminal_text = tk.Text(frame, bg=style_bg, fg=style_fg, insertbackground="#ffffff", font=("Consolas", 12), wrap='word', borderwidth=0, highlightthickness=0)
        self.terminal_text.pack(side=tk.TOP, expand=True, fill="both")
        
        # 启用滚动条
        scrollbar = ttk.Scrollbar(frame, command=self.terminal_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.terminal_text.config(yscrollcommand=scrollbar.set)
        
        # 插入欢迎信息
        self.insert_welcome_message()
        
        # 历史命令列表
        self.history_commands = []
        self.history_index = -1
        
        # 创建一个Entry widget for command input
        self.entry = ttk.Entry(self)
        self.entry.pack(fill="x", padx=10, pady=(0, 10))
        
        # 弹出菜单
        self.popup_menu = tk.Menu(self.terminal_text, tearoff=0)
        self.popup_menu.add_command(label="复制", command=lambda: self.terminal_text.event_generate("<<Copy>>"))
        self.popup_menu.add_command(label="粘贴", command=lambda: self.terminal_text.event_generate("<<Paste>>"))
        self.popup_menu.add_command(label="剪切", command=lambda: self.terminal_text.event_generate("<<Cut>>"))
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="清屏", command=self.clear_screen)
        self.popup_menu.add_command(label="编辑命令", command=self.on_edit_command_click)
        
        self.terminal_text.bind("<Button-3>", self.show_popup)
    
    def set_controller(self, controller):
        self.controller = controller
        self.entry.bind("<Return>", self.controller.handle_return)
        self.entry.bind("<Up>", lambda event: self.controller.move_to_history(-1))
        self.entry.bind("<Down>", lambda event: self.controller.move_to_history(1))

    def insert_welcome_message(self):
        """Insert the welcome message into the terminal text widget."""
        self.terminal_text.insert(tk.END, "Foxes的玩具集\n", ("welcome",))
        self.terminal_text.tag_configure("prompt", foreground="#9cdcfe")
        self.terminal_text.insert(tk.END, "┌──(fox㉿foxes)-[~]\n└─$", "prompt")
        self.terminal_text.mark_set("input_start", "end-1c")
        self.terminal_text.see(tk.END)
        self.terminal_text.tag_configure("welcome", foreground="#569cd6", font=("Consolas", 14, "bold"))
    
    def insert_output(self, text, tag=None):
        """Insert output text into the terminal text widget."""
        self.terminal_text.insert(tk.END, "\n")
        self.terminal_text.insert(tk.END, f"{text}\n", tag)
    
    def clear_screen(self):
        """Clear all text except the welcome message and the last prompt."""
        self.terminal_text.delete("1.0", "input_start")
        self.terminal_text.see(tk.END)
    
    def insert_prompt(self):
        """Insert the prompt into the terminal text widget."""
        self.terminal_text.insert(tk.END, "┌──(fox㉿foxes)-[~]\n└─$", "prompt")
        self.terminal_text.mark_set("input_start", "end-1c")
        self.terminal_text.see(tk.END)

    def show_popup(self, event):
        """Show the popup menu."""
        try:
            self.popup_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.popup_menu.grab_release()

    def on_edit_command_click(self):
        """Handle the click event for editing commands."""
        if self.controller:
            self.controller.edit_command()

class TerminalController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
    
    def handle_return(self, event=None):
        """Handle the Enter key press in the entry widget."""
        user_input = self.view.entry.get().strip()
        if user_input and (not self.view.history_commands or user_input != self.view.history_commands[-1]):
            self.view.history_commands.append(user_input)
            self.view.history_index = len(self.view.history_commands) - 1
        
        self.view.insert_output(f"{user_input}")
        
        if user_input in self.model.get_commands():
            self.execute_custom_command(user_input)
        else:
            self.view.insert_output(f"未知命令: {user_input}", "error")
        
        self.view.entry.delete(0, tk.END)
        self.view.insert_prompt()
    
    def move_to_history(self, direction):
        """Move through command history using Up and Down keys."""
        current_input = self.view.entry.get().strip()
        if direction == -1:
            if self.view.history_index > 0:
                self.view.history_index -= 1
        elif direction == 1:
            if self.view.history_index < len(self.view.history_commands) - 1:
                self.view.history_index += 1
        
        if self.view.history_index >= 0 and self.view.history_index < len(self.view.history_commands):
            new_input = self.view.history_commands[self.view.history_index]
        else:
            new_input = ""
        
        self.view.entry.delete(0, tk.END)
        self.view.entry.insert(0, new_input)
    
    def clear_screen(self):
        """Clear all text except the welcome message and the last prompt."""
        self.view.clear_screen()
    
    def edit_command(self):
        """Open a window to edit custom commands."""
        edit_window = tk.Toplevel(self.view)
        edit_window.title("编辑命令")
        edit_window.geometry("400x350")
        
        listbox = tk.Listbox(edit_window, bg="#2b2b2b", fg="#d4d4d4", font=("Consolas", 12))
        listbox.pack(side=tk.LEFT, expand=True, fill="both")
        
        for command in self.model.get_commands():
            listbox.insert(tk.END, command)
        
        def on_select(event):
            try:
                index = listbox.curselection()[0]
                selected_command = listbox.get(index)
                entry.delete(0, tk.END)
                entry.insert(0, selected_command)
                path_entry.delete(0, tk.END)
                path_entry.insert(0, self.model.get_commands()[selected_command]['path'])
                env_var.set(self.model.get_commands()[selected_command]['env'])
                if self.model.get_commands()[selected_command].get('custom_env'):
                    custom_env_entry.delete(0, tk.END)
                    custom_env_entry.insert(0, self.model.get_commands()[selected_command]['custom_env'])
            except IndexError:
                pass
        
        listbox.bind('<<ListboxSelect>>', on_select)
        
        button_frame = tk.Frame(edit_window, bg="#2b2b2b")
        button_frame.pack(side=tk.RIGHT, fill="y")
        
        entry = ttk.Entry(edit_window)
        entry.pack(pady=5, padx=10, fill="x")
        
        path_entry = ttk.Entry(edit_window)
        path_entry.pack(pady=5, padx=10, fill="x")
        
        browse_button = ttk.Button(edit_window, text="浏览...", command=lambda: self.browse_file(path_entry))
        browse_button.pack(pady=5, padx=10, fill="x")
        
        env_var = tk.StringVar(value="cmd")
        env_label = ttk.Label(edit_window, text="运行环境:")
        env_label.pack(pady=5, padx=10, anchor="w")
        env_dropdown = ttk.Combobox(edit_window, textvariable=env_var, values=["cmd", "powershell", "custom"])
        env_dropdown.pack(pady=5, padx=10, fill="x")
        
        custom_env_entry = ttk.Entry(edit_window)
        custom_env_entry.pack(pady=5, padx=10, fill="x")
        custom_env_entry.config(state="disabled")
        
        def enable_custom_env(*args):
            if env_var.get() == "custom":
                custom_env_entry.config(state="normal")
            else:
                custom_env_entry.config(state="disabled")
        
        env_var.trace("w", enable_custom_env)
        
        def add_command():
            command_name = entry.get().strip()
            command_path = path_entry.get().strip()
            env_choice = env_var.get()
            custom_env = custom_env_entry.get().strip() if env_var.get() == "custom" else None
            
            if not command_name or not command_path:
                messagebox.showwarning("警告", "请输入有效的命令名称和路径")
                return
            
            if self.model.add_command(command_name, command_path, env_choice, custom_env):
                listbox.insert(tk.END, command_name)
                entry.delete(0, tk.END)
                path_entry.delete(0, tk.END)
                env_var.set("cmd")
                custom_env_entry.delete(0, tk.END)
        
        def delete_command():
            try:
                index = listbox.curselection()[0]
                selected_command = listbox.get(index)
                if self.model.delete_command(selected_command):
                    listbox.delete(index)
                    entry.delete(0, tk.END)
                    path_entry.delete(0, tk.END)
                    env_var.set("cmd")
                    custom_env_entry.delete(0, tk.END)
            except IndexError:
                messagebox.showwarning("警告", "请选择一个命令进行删除")
        
        def modify_command():
            try:
                index = listbox.curselection()[0]
                command_name = entry.get().strip()
                command_path = path_entry.get().strip()
                env_choice = env_var.get()
                custom_env = custom_env_entry.get().strip() if env_var.get() == "custom" else None
                
                if not command_name or not command_path:
                    messagebox.showwarning("警告", "请输入有效的命令名称和路径")
                    return
                
                old_command_name = listbox.get(index)
                if self.model.modify_command(old_command_name, command_name, command_path, env_choice, custom_env):
                    listbox.delete(index)
                    listbox.insert(index, command_name)
                    entry.delete(0, tk.END)
                    path_entry.delete(0, tk.END)
                    env_var.set("cmd")
                    custom_env_entry.delete(0, tk.END)
            except IndexError:
                messagebox.showwarning("警告", "请选择一个命令进行修改")
        
        add_button = ttk.Button(button_frame, text="添加", command=add_command)
        add_button.pack(pady=5, padx=10, fill="x")
        
        delete_button = ttk.Button(button_frame, text="删除", command=delete_command)
        delete_button.pack(pady=5, padx=10, fill="x")
        
        modify_button = ttk.Button(button_frame, text="修改", command=modify_command)
        modify_button.pack(pady=5, padx=10, fill="x")
    
    def browse_file(self, entry_widget):
        """Browse for executable files."""
        file_path = filedialog.askopenfilename(title="选择可执行文件")
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)
    
    def execute_custom_command(self, command):
        """Execute a custom command."""
        try:
            command_info = self.model.get_commands()[command]
            command_path = command_info['path']
            env_choice = command_info['env']
            custom_env = command_info['custom_env']
            
            if not os.path.isfile(command_path):
                self.view.insert_output(f"命令路径不存在: {command_path}", "error")
                return
            
            if env_choice == "cmd":
                result = subprocess.run(["cmd", "/c", command_path], capture_output=True, text=True, check=True)
            elif env_choice == "powershell":
                result = subprocess.run(["powershell", "-File", command_path], capture_output=True, text=True, check=True)
            elif env_choice == "custom" and custom_env:
                result = subprocess.run([custom_env, command_path], capture_output=True, text=True, check=True)
            else:
                self.view.insert_output("无效的运行环境设置", "error")
                return
            
            self.view.insert_output(result.stdout + "\n")
            self.view.insert_output(result.stderr + "\n", "error")
        except FileNotFoundError:
            self.view.insert_output(f"找不到命令: {command}", "error")
        except PermissionError:
            self.view.insert_output(f"没有权限执行命令: {command}", "error")
        except Exception as e:
            self.view.insert_output(f"执行命令 {command} 时出错: {str(e)}", "error")
        finally:
            self.view.insert_prompt()

def main():
    model = CommandModel()
    view = TerminalView(controller=None)
    controller = TerminalController(model, view)
    view.set_controller(controller)
    view.mainloop()

if __name__ == "__main__":
    main()