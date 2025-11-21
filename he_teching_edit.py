import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import shutil
from datetime import datetime

class ExamDataEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("考试数据编辑器")
        self.root.geometry("900x650")  # 增加宽度以容纳多选框
        self.icon('favicon.ico')
        
        # 数据存储
        self.exam_data = []
        self.current_file = None
        
        # 创建界面
        self.create_widgets()
        self.load_default_data()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置行和列的权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 顶部按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(button_frame, text="新建", command=self.new_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="打开", command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="保存", command=self.save_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="另存为", command=self.save_as_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="添加考试", command=self.add_exam).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="删除选中", command=self.delete_exam).pack(side=tk.LEFT)
        
        # 当前文件标签
        self.file_label = ttk.Label(button_frame, text="未保存的文件")
        self.file_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 考试列表框架
        list_frame = ttk.LabelFrame(main_frame, text="考试列表", padding="5")
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 考试列表 - 添加多选框列
        columns = ("selected", "subject", "date", "time", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题
        self.tree.heading("selected", text="选择")
        self.tree.heading("subject", text="考试科目")
        self.tree.heading("date", text="考试日期")
        self.tree.heading("time", text="考试时间")
        self.tree.heading("status", text="状态")
        
        # 设置列宽
        self.tree.column("selected", width=50, anchor="center")
        self.tree.column("subject", width=150)
        self.tree.column("date", width=100)
        self.tree.column("time", width=100)
        self.tree.column("status", width=80)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 绑定事件
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-1>", self.on_tree_click)  # 添加点击事件处理多选框
        
        # 编辑框架
        edit_frame = ttk.LabelFrame(main_frame, text="考试信息编辑", padding="10")
        edit_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        edit_frame.columnconfigure(1, weight=1)
        
        # 表单字段
        ttk.Label(edit_frame, text="考试科目:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.subject_var = tk.StringVar()
        self.subject_entry = ttk.Entry(edit_frame, textvariable=self.subject_var, width=30)
        self.subject_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(edit_frame, text="考试日期:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.date_var = tk.StringVar()
        self.date_entry = ttk.Entry(edit_frame, textvariable=self.date_var, width=30)
        self.date_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        ttk.Button(edit_frame, text="今天", command=self.set_today_date, width=6).grid(row=1, column=2, padx=(5, 0))
        
        ttk.Label(edit_frame, text="开始时间:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.start_time_var = tk.StringVar()
        self.start_time_entry = ttk.Entry(edit_frame, textvariable=self.start_time_var, width=30)
        self.start_time_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(edit_frame, text="结束时间:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.end_time_var = tk.StringVar()
        self.end_time_entry = ttk.Entry(edit_frame, textvariable=self.end_time_var, width=30)
        self.end_time_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2, padx=(5, 0))
        
        ttk.Label(edit_frame, text="试卷信息:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.paper_info_text = tk.Text(edit_frame, width=30, height=8)
        self.paper_info_text.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2, padx=(5, 0))
        
        # 按钮框架
        form_button_frame = ttk.Frame(edit_frame)
        form_button_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(form_button_frame, text="保存", command=self.save_exam).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(form_button_frame, text="清空", command=self.clear_form).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(form_button_frame, text="生成示例", command=self.generate_sample).pack(side=tk.LEFT)
        
        # 全选/取消全选按钮
        select_frame = ttk.Frame(main_frame)
        select_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        ttk.Button(select_frame, text="全选", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(select_frame, text="取消全选", command=self.deselect_all).pack(side=tk.LEFT)
        
        copyright_label = ttk.Label(select_frame, text="Powered by wkx2009", foreground="gray")
        copyright_label.pack(side=tk.LEFT, padx=(200, 0))

        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 当前编辑的索引
        self.editing_index = None

    def load_default_data(self):
        """加载默认的示例数据"""
        self.exam_data = [
            {
                "subject": "示例",
                "date": "1145-1-4",
                "startTime": "09:00",
                "endTime": "11:00",
                "paperInfo": "该试卷共xx张xx页xx道大题"
            }
        ]
        self.refresh_list()

    def refresh_list(self):
        """刷新考试列表"""
        # 清空列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加数据
        for i, exam in enumerate(self.exam_data):
            # 计算状态
            status = self.calculate_exam_status(exam["date"], exam["startTime"], exam["endTime"])
            # 添加到列表，第一列为空（未选中）
            self.tree.insert("", "end", values=(
                "",  # 选择列初始为空
                exam["subject"],
                exam["date"],
                f"{exam['startTime']}-{exam['endTime']}",
                status
            ))

    def calculate_exam_status(self, date, start_time, end_time):
        """计算考试状态"""
        try:
            now = datetime.now()
            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            
            if now < start_datetime:
                return "即将开始"
            elif start_datetime <= now <= end_datetime:
                return "进行中"
            else:
                return "已结束"
        except Exception as e:
            print(f"计算状态错误: {e}")
            return "未知"

    def on_tree_click(self, event):
        """处理树状视图点击事件，实现多选框功能"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            
            # 如果点击的是选择列
            if column == "#1":  # 选择列
                current_value = self.tree.set(item, "selected")
                new_value = "✓" if current_value == "" else ""
                self.tree.set(item, "selected", new_value)

    def select_all(self):
        """全选"""
        for item in self.tree.get_children():
            self.tree.set(item, "selected", "✓")
        self.status_var.set("已全选所有项目")

    def deselect_all(self):
        """取消全选"""
        for item in self.tree.get_children():
            self.tree.set(item, "selected", "")
        self.status_var.set("已取消全选")

    def new_file(self):
        """新建文件"""
        self.exam_data = []
        self.current_file = None
        self.file_label.config(text="未保存的文件")
        self.refresh_list()
        self.clear_form()
        self.status_var.set("已创建新文件")

    def open_file(self):
        """打开文件"""
        filename = filedialog.askopenfilename(
            title="打开JSON文件",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if not isinstance(data, list):
                    raise ValueError("JSON文件应该包含一个数组")
                
                self.exam_data = data
                self.current_file = filename
                self.file_label.config(text=os.path.basename(filename))
                self.refresh_list()
                self.clear_form()
                self.status_var.set(f"已加载文件: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"无法打开文件:\n{str(e)}")

    def save_file(self):
        """保存文件"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_as_file()

    def save_as_file(self):
        """另存为文件"""
        filename = filedialog.asksaveasfilename(
            title="保存JSON文件",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if filename:
            self._save_to_file(filename)
            self.current_file = filename
            self.file_label.config(text=os.path.basename(filename))

    def _save_to_file(self, filename):
        """保存数据到文件，带有备份功能"""
        try:
            # 如果文件已存在，先创建备份
            if os.path.exists(filename):
                backup_name = filename + '.bak'
                try:
                    shutil.copy2(filename, backup_name)
                except Exception as e:
                    print(f"创建备份失败: {e}")
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.exam_data, f, ensure_ascii=False, indent=2)
            self.status_var.set(f"文件已保存: {filename}")
        except Exception as e:
            messagebox.showerror("错误", f"无法保存文件:\n{str(e)}")

    def add_exam(self):
        """添加新考试"""
        self.clear_form()
        self.editing_index = None
        self.status_var.set("准备添加新考试")

    def delete_exam(self):
        """删除选中的考试"""
        selected_items = []
        for item in self.tree.get_children():
            if self.tree.set(item, "selected") == "✓":
                selected_items.append(item)
        
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要删除的考试（点击第一列的选择框）")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected_items)} 个考试吗？"):
            # 通过科目名称和日期来匹配数据
            items_to_delete = []
            for item in selected_items:
                values = self.tree.item(item)['values']
                subject = values[1]  # 科目在第2列
                date = values[2]     # 日期在第3列
                
                # 找到对应的数据索引
                for i, exam in enumerate(self.exam_data):
                    if exam['subject'] == subject and exam['date'] == date:
                        items_to_delete.append(i)
                        break
            
            # 从大到小排序，避免删除时索引变化
            items_to_delete.sort(reverse=True)
            
            deleted_count = 0
            for index in items_to_delete:
                if 0 <= index < len(self.exam_data):
                    del self.exam_data[index]
                    deleted_count += 1
            
            self.refresh_list()
            self.clear_form()
            self.status_var.set(f"已删除 {deleted_count} 个考试")

    def on_item_double_click(self, event):
        """双击列表项进行编辑"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            # 如果不是点击选择列，则进行编辑
            if column != "#1":
                item = self.tree.identify_row(event.y)
                if item:
                    self.edit_selected_exam(item)

    def edit_selected_exam(self, item):
        """编辑选中的考试"""
        values = self.tree.item(item)['values']
        subject = values[1]  # 科目在第2列
        date = values[2]     # 日期在第3列
        
        # 找到对应的数据索引
        for i, exam in enumerate(self.exam_data):
            if exam['subject'] == subject and exam['date'] == date:
                self.editing_index = i
                exam = self.exam_data[i]
                
                # 填充表单
                self.subject_var.set(exam["subject"])
                self.date_var.set(exam["date"])
                self.start_time_var.set(exam["startTime"])
                self.end_time_var.set(exam["endTime"])
                self.paper_info_text.delete(1.0, tk.END)
                self.paper_info_text.insert(1.0, exam["paperInfo"])
                
                self.status_var.set(f"正在编辑: {exam['subject']}")
                break

    def save_exam(self):
        """保存考试信息"""
        # 获取表单数据
        subject = self.subject_var.get().strip()
        date = self.date_var.get().strip()
        start_time = self.start_time_var.get().strip()
        end_time = self.end_time_var.get().strip()
        paper_info = self.paper_info_text.get(1.0, tk.END).strip()
        
        # 验证数据
        if not all([subject, date, start_time, end_time, paper_info]):
            messagebox.showwarning("警告", "请填写所有字段")
            return
        
        # 验证日期格式
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("警告", "日期格式不正确，请使用 YYYY-MM-DD 格式")
            return
        
        # 验证时间格式
        try:
            datetime.strptime(start_time, "%H:%M")
            datetime.strptime(end_time, "%H:%M")
        except ValueError:
            messagebox.showwarning("警告", "时间格式不正确，请使用 HH:MM 格式")
            return
        
        # 创建考试对象
        exam = {
            "subject": subject,
            "date": date,
            "startTime": start_time,
            "endTime": end_time,
            "paperInfo": paper_info
        }
        
        # 保存或更新
        if self.editing_index is not None:
            # 更新现有考试
            self.exam_data[self.editing_index] = exam
            self.status_var.set(f"已更新: {subject}")
        else:
            # 添加新考试
            self.exam_data.append(exam)
            self.status_var.set(f"已添加: {subject}")
        
        self.refresh_list()
        self.clear_form()

    def clear_form(self):
        """清空表单"""
        self.subject_var.set("")
        self.date_var.set("")
        self.start_time_var.set("")
        self.end_time_var.set("")
        self.paper_info_text.delete(1.0, tk.END)
        self.editing_index = None
        self.status_var.set("表单已清空")

    def set_today_date(self):
        """设置今天日期"""
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_var.set(today)
        self.status_var.set("已设置为今天日期")

    def generate_sample(self):
        """生成示例数据"""
        samples = [
            {
                "subject": "数学",
                "date": "2024-01-15",
                "startTime": "09:00",
                "endTime": "11:00",
                "paperInfo": "该试卷共2张4页6道大题，总分100分"
            },
            {
                "subject": "英语",
                "date": "2024-01-16",
                "startTime": "14:00",
                "endTime": "16:00",
                "paperInfo": "该试卷共2张3页5道大题，总分120分"
            }
        ]
        
        self.exam_data.extend(samples)
        self.refresh_list()
        self.status_var.set("已添加示例数据")

def main():
    root = tk.Tk()
    app = ExamDataEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()