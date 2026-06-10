import tkinter as tk
from tkinter import messagebox, ttk
from fractions import Fraction


class LinearEquationSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("线性方程组求解器")
        self.root.geometry("950x1100")
        self.root.resizable(True, True)  # 允许调整窗口大小
        
        # 创建渐变背景
        self.create_gradient_background()
        
        self.is_homogeneous = False  # 是否为齐次方程
        self.num_equations = 3
        self.num_variables = 3
        self.equation_entries = []
        
        # 创建界面
        self.create_header()
        self.create_main_container()  # 创建主容器（左右分栏）
        
        # 延迟初始化
        self.root.after(100, self.update_input_fields)
    
    def create_gradient_background(self):
        """创建粉红色到淡蓝色的渐变背景"""
        # 创建一个Canvas作为背景
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # 绘制渐变背景
        def draw_gradient(event=None):
            self.bg_canvas.delete("gradient")
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            
            if width > 1 and height > 1:
                for i in range(height):
                    # 从粉红色 (#FFB6C1) 到淡蓝色 (#87CEEB) 的渐变
                    r = int(255 - (255 - 135) * i / height)
                    g = int(182 + (206 - 182) * i / height)
                    b = int(193 + (235 - 193) * i / height)
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    self.bg_canvas.create_line(0, i, width, i, fill=color, width=1, tags="gradient")
        
        # 绑定窗口大小变化事件
        self.root.bind('<Configure>', draw_gradient)
        # 立即绘制一次
        self.root.after(100, draw_gradient)
    
    def create_header(self):
        """创建标题区域"""
        # 创建透明背景的标题框架
        header_frame = tk.Frame(self.root, bg="#f5f5f5", pady=15)
        header_frame.pack(fill="x", padx=20)
        
        # 创建一个容器Frame来放置Canvas和按钮
        container_frame = tk.Frame(header_frame, bg="#f5f5f5")
        container_frame.pack(fill="x")
        
        # 创建标题Canvas（占据大部分空间）
        self.header_canvas = tk.Canvas(container_frame, height=70, bg="white", highlightthickness=0)
        self.header_canvas.pack(side="left", fill="x", expand=True)
        
        # 绑定Canvas大小变化事件，动态重绘背景和标题
        self.header_canvas.bind('<Configure>', self._draw_header_background)
        
        # 初始绘制
        self.root.after(100, lambda: self._draw_header_background(None))
        
        # 添加联系开发者按钮（放在右侧）
        contact_btn = tk.Button(
            container_frame,
            text="联系开发者",
            font=("Microsoft YaHei", 12, "bold"),
            bg="#3498db",
            fg="white",
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=15,
            pady=5,
            command=self.show_contact_info
        )
        contact_btn.pack(side="right", padx=(10, 0), pady=10)
    
    def _draw_header_background(self, event=None):
        """绘制标题区域的渐变背景和居中文字"""
        canvas = self.header_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1 or height <= 1:
            return
        
        # 绘制渐变背景
        for i in range(width):
            # 从淡粉色 (#FFE4E1) 到淡蓝色 (#E0F7FA) 的渐变
            r = int(255 - (255 - 224) * i / width)
            g = int(228 + (247 - 228) * i / width)
            b = int(225 + (250 - 225) * i / width)
            color = f"#{r:02x}{g:02x}{b:02x}"
            canvas.create_line(i, 0, i, height, fill=color, width=1)
        
        # 在Canvas正中央添加标题（使用anchor='center'确保居中）
        center_x = width // 2
        canvas.create_text(center_x, 28, text="线性方程组求解器", 
                           font=("Microsoft YaHei", 28, "bold"), fill="#2c3e50",
                           anchor="center")
        canvas.create_text(center_x, 52, text="支持齐次/非齐次线性方程组 · 自动检测自由变量 · 最简分数形式", 
                           font=("Microsoft YaHei", 13), fill="#7f8c8d",
                           anchor="center")
    
    def create_main_container(self):
        """创建主容器（左右分栏）"""
        # 使用固定比例的主容器
        main_container = tk.Frame(self.root, bg="#f5f5f5")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # 配置列权重：左侧45%，右侧55%
        main_container.grid_columnconfigure(0, weight=45)
        main_container.grid_columnconfigure(1, weight=55)
        main_container.grid_rowconfigure(0, weight=1)
        
        # 左侧面板（配置、答案输入、方程输入）
        left_frame = tk.Frame(main_container, bg="#f5f5f5")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # 右侧面板（解答结果显示）
        right_frame = tk.Frame(main_container, bg="#ffffff")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        # 在左侧面板创建各部分
        self.create_config_section(left_frame)
        self.create_answer_section(left_frame)
        self.create_input_section(left_frame)
        
        # 在右侧面板创建解答显示
        self.create_solution_display(right_frame)
    
    def create_config_section(self, parent):
        """创建配置区域"""
        config_frame = tk.Frame(parent, bg="#ffffff", padx=20, pady=15)
        config_frame.pack(fill="x", pady=8)
        
        # 第一行：齐次/非齐次选择
        homo_label = tk.Label(
            config_frame,
            text="方程类型：",
            font=("Microsoft YaHei", 14, "bold"),
            fg="#2c3e50",
            bg="#ffffff"
        )
        homo_label.grid(row=0, column=0, sticky="w", pady=8)
        
        self.homo_var = tk.BooleanVar(value=False)
        homo_check = tk.Checkbutton(
            config_frame,
            text="齐次方程组 (Ax=0)",
            variable=self.homo_var,
            font=("Microsoft YaHei", 13),
            fg="#e74c3c",
            bg="#ffffff",
            selectcolor="#ecf0f1",
            activebackground="#ffffff",
            command=self.on_homogeneous_change
        )
        homo_check.grid(row=0, column=1, sticky="w", padx=10, pady=8)
        
        # 第二行：方程数量和变量数量
        eq_label = tk.Label(
            config_frame,
            text="方程数量：",
            font=("Microsoft YaHei", 14, "bold"),
            fg="#2c3e50",
            bg="#ffffff"
        )
        eq_label.grid(row=1, column=0, sticky="w", pady=8)
        
        self.eq_var = tk.StringVar(value="3")
        eq_combo = ttk.Combobox(
            config_frame,
            textvariable=self.eq_var,
            values=["1", "2", "3", "4", "5"],
            state="readonly",
            font=("Arial", 14),
            width=8
        )
        eq_combo.grid(row=1, column=1, sticky="w", padx=10, pady=8)
        eq_combo.bind('<<ComboboxSelected>>', lambda e: self.update_input_fields())
        
        var_label = tk.Label(
            config_frame,
            text="未知量个数：",
            font=("Microsoft YaHei", 14, "bold"),
            fg="#2c3e50",
            bg="#ffffff"
        )
        var_label.grid(row=1, column=2, sticky="w", pady=8, padx=(30, 0))
        
        self.var_var = tk.StringVar(value="3")
        var_combo = ttk.Combobox(
            config_frame,
            textvariable=self.var_var,
            values=["1", "2", "3", "4", "5"],
            state="readonly",
            font=("Arial", 14),
            width=8
        )
        var_combo.grid(row=1, column=3, sticky="w", padx=10, pady=8)
        var_combo.bind('<<ComboboxSelected>>', lambda e: self.update_input_fields())
        
        # 清空按钮
        clear_btn = tk.Button(
            config_frame,
            text="清空重置",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#e74c3c",
            fg="white",
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=15,
            pady=8,
            command=self.clear_all
        )
        clear_btn.grid(row=1, column=4, sticky="w", padx=5, pady=8)
        
        # 加载示例按钮
        example_btn = tk.Button(
            config_frame,
            text="加载示例",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#9b59b6",
            fg="white",
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=15,
            pady=8,
            command=self.load_example
        )
        example_btn.grid(row=1, column=5, sticky="w", padx=5, pady=8)
    
    def create_answer_section(self, parent):
        """创建用户答案输入区域"""
        answer_frame = tk.Frame(parent, bg="#ffffff", padx=20, pady=15)
        answer_frame.pack(fill="x", pady=8)
        
        # 标题
        title_label = tk.Label(
            answer_frame,
            text="请输入你的答案（可选，留空直接看解答）",
            font=("Microsoft YaHei", 14, "bold"),
            fg="#2c3e50",
            bg="#ffffff"
        )
        title_label.pack(anchor="w", pady=(0, 15))
        
        # 创建带双向滚动条的答案输入容器
        answer_scroll_frame = tk.Frame(answer_frame, bg="#ffffff")
        answer_scroll_frame.pack(fill="both", expand=True)
        
        # 创建Canvas和双向滚动条
        answer_canvas = tk.Canvas(answer_scroll_frame, bg="#ffffff", highlightthickness=0, height=200)
        v_scrollbar = tk.Scrollbar(answer_scroll_frame, orient="vertical", command=answer_canvas.yview)
        h_scrollbar = tk.Scrollbar(answer_scroll_frame, orient="horizontal", command=answer_canvas.xview)
        
        # 答案输入容器（放在Canvas内）
        self.answer_container = tk.Frame(answer_canvas, bg="#ffffff")
        
        answer_canvas.create_window((0, 0), window=self.answer_container, anchor="nw")
        answer_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # 使用grid布局
        answer_canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # 配置网格权重
        answer_scroll_frame.grid_rowconfigure(0, weight=1)
        answer_scroll_frame.grid_columnconfigure(0, weight=1)
        
        # 更新滚动区域
        self.answer_container.bind("<Configure>", lambda e: answer_canvas.configure(scrollregion=answer_canvas.bbox("all")))
        
        # 绑定鼠标滚轮进行垂直滚动
        def on_mousewheel(event):
            answer_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        answer_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 答案输入框列表
        self.answer_entries = []
        # 自由变量复选框列表
        self.free_var_checkboxes = []
        # 系数输入框字典：{主元变量索引: {自由变量索引: Entry, 'const': Entry}}
        self.coefficient_entries = {}
        
        # 提交答案按钮
        self.submit_btn = tk.Button(
            answer_frame,
            text="提交答案",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#27ae60",
            fg="white",
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self.check_answer
        )
        self.submit_btn.pack(side="left", padx=(0, 10), pady=10)
        
        # 显示答案按钮
        self.show_answer_btn = tk.Button(
            answer_frame,
            text="显示答案",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#3498db",
            fg="white",
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self.show_solution
        )
        self.show_answer_btn.pack(side="left", padx=(0, 10), pady=10)
        
        # 无解按钮
        self.no_solution_btn = tk.Button(
            answer_frame,
            text="无解",
            font=("Microsoft YaHei", 13, "bold"),
            bg="#e74c3c",
            fg="white",
            relief="raised",
            bd=2,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self.mark_no_solution
        )
        self.no_solution_btn.pack(side="left", pady=10)
        
        # 反馈标签
        self.feedback_label = tk.Label(
            answer_frame,
            text="",
            font=("Microsoft YaHei", 14),
            fg="#27ae60",
            bg="#ffffff"
        )
        self.feedback_label.pack(anchor="w", pady=(10, 0))
        
        # 添加使用提示
        tip_label = tk.Label(
            answer_frame,
            text="💡 提示：\n方程无解时点击'无解'按钮\n有自由变量时勾选'自由'按钮\n系统会自动弹出系数输入框，请输入各自由变量的系数和常数项",
            font=("Microsoft YaHei", 12),
            fg="#7f8c8d",
            bg="#ffffff",
            justify="left"
        )
        tip_label.pack(anchor="w", pady=(8, 0))
    
    def on_homogeneous_change(self):
        """齐次方程切换事件"""
        self.is_homogeneous = self.homo_var.get()
        self.update_input_fields()
    
    def on_free_var_change(self, var_index):
        """自由变量复选框变化事件"""
        # 延迟执行，等待所有复选框状态更新完成
        self.root.after(100, self.update_coefficient_entries)
    
    def update_coefficient_entries(self):
        """根据自由变量的选择更新系数输入框"""
        # 获取当前勾选的自由变量
        free_vars = [i for i, cb in enumerate(self.free_var_checkboxes) if cb.get()]
        
        # 清除旧的系数输入框
        for widget in self.answer_container.winfo_children():
            # 只删除系数输入框容器，保留原始的答案输入框和复选框
            if hasattr(widget, 'winfo_class') and widget.winfo_class() == 'Frame':
                # 检查是否是系数输入框容器（通过tag判断）
                if hasattr(widget, '_is_coeff_frame') and widget._is_coeff_frame:
                    widget.destroy()
        
        self.coefficient_entries = {}
        
        # 如果没有自由变量，不需要创建系数输入框
        if not free_vars:
            return
        
        # 为非自由变量创建系数输入框
        for j in range(self.num_variables):
            if j not in free_vars:
                # 这是主元变量，需要创建系数输入框
                coeff_frame = tk.Frame(self.answer_container, bg="#ffffff")
                coeff_frame._is_coeff_frame = True  # 标记为系数输入框容器
                coeff_frame.pack(side="left", padx=8, pady=5)
                
                # 显示变量名
                var_names = ['x₁', 'x₂', 'x₃', 'x₄', 'x₅']
                label = tk.Label(
                    coeff_frame,
                    text=f"{var_names[j]} =",
                    font=("Microsoft YaHei", 9, "bold"),
                    fg="#27ae60",
                    bg="#ffffff"
                )
                label.pack(anchor="w", pady=(0, 3))
                
                # 为每个自由变量创建系数输入框
                self.coefficient_entries[j] = {}
                for free_idx in free_vars:
                    coeff_row = tk.Frame(coeff_frame, bg="#ffffff")
                    coeff_row.pack(fill="x", pady=2)
                    
                    # 自由变量标签
                    free_label = tk.Label(
                        coeff_row,
                        text=f"{var_names[free_idx]} 系数:",
                        font=("Microsoft YaHei", 10),
                        fg="#7f8c8d",
                        bg="#ffffff"
                    )
                    free_label.pack(side="left", padx=(0, 3))
                    
                    # 系数输入框
                    coeff_entry = tk.Entry(
                        coeff_row,
                        font=("Arial", 12),
                        bg="#ffffff",
                        fg="#2c3e50",
                        relief="solid",
                        bd=1,
                        width=8,
                        justify="center"
                    )
                    coeff_entry.pack(side="left")
                    coeff_entry.insert(0, "0")
                    self.coefficient_entries[j][free_idx] = coeff_entry
                
                # 常数项输入框
                const_row = tk.Frame(coeff_frame, bg="#ffffff")
                const_row.pack(fill="x", pady=2)
                
                const_label = tk.Label(
                    const_row,
                    text="常数项:",
                    font=("Microsoft YaHei", 10),
                    fg="#7f8c8d",
                    bg="#ffffff"
                )
                const_label.pack(side="left", padx=(0, 3))
                
                const_entry = tk.Entry(
                    const_row,
                    font=("Arial", 12),
                    bg="#ffffff",
                    fg="#2c3e50",
                    relief="solid",
                    bd=1,
                    width=8,
                    justify="center"
                )
                const_entry.pack(side="left")
                const_entry.insert(0, "0")
                self.coefficient_entries[j]['const'] = const_entry
    
    def check_answer(self):
        """检查用户答案"""
        # 先求解方程组
        try:
            matrix, constants = self.parse_coefficients()
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return
        
        # 求解
        augmented, pivot_cols, steps = self.gauss_elimination(matrix, constants)
        n = len(matrix)
        m = len(matrix[0])
        rank = len(pivot_cols)
        
        # 检查是否有解
        has_contradiction = False
        if not self.is_homogeneous:
            for i in range(rank, n):
                if augmented[i][-1] != 0:
                    has_contradiction = True
                    break
        
        # 如果无解
        if has_contradiction:
            self.feedback_label.config(text="✗ 答案错误！该方程组无解，点击'无解'按钮", fg="#e74c3c")
            # 延迟1秒后显示解答，让用户有时间看清错误提示
            self.root.after(1500, self.show_solution)
            return
        
        # 获取用户标记的自由变量
        user_free_vars = [i for i, cb in enumerate(self.free_var_checkboxes) if cb.get()]
        
        # 检查是否有自由变量
        num_free_vars = m - rank
        
        if num_free_vars > 0:
            # 有自由变量的情况
            # 找出系统确定的自由变量
            system_free_vars = []
            for j in range(m):
                if j not in pivot_cols:
                    system_free_vars.append(j)
            
            # 首先检查用户是否正确标记了自由变量
            if set(user_free_vars) != set(system_free_vars):
                if len(user_free_vars) == 0:
                    self.feedback_label.config(
                        text="⚠ 方程组有无穷多解，请勾选自由变量", 
                        fg="#f39c12"
                    )
                else:
                    self.feedback_label.config(
                        text="✗ 自由变量标记有误，正确答案如下：", 
                        fg="#e74c3c"
                    )
                    # 延迟1.5秒后显示解答
                    self.root.after(1500, self.show_solution)
                return
            
            # 用户正确标记了自由变量，现在检查系数输入
            if not self.coefficient_entries:
                # 没有系数输入框，只判定自由变量正确
                self.feedback_label.config(
                    text="✓ 太棒了！你正确识别了自由变量！点击查看完整通解", 
                    fg="#27ae60"
                )
                return
            
            # 构建系统的通解表达式
            # augmented矩阵已经是行最简形式
            solution_expr = {}
            for i in range(rank):
                pivot_col = pivot_cols[i]
                # 主元变量的表达式
                expr = {'const': augmented[i][-1], 'coeffs': {}}
                for free_idx in system_free_vars:
                    expr['coeffs'][free_idx] = -augmented[i][free_idx]
                solution_expr[pivot_col] = expr
            
            # 检查用户输入的系数
            all_correct = True
            for pivot_col, user_coeffs in self.coefficient_entries.items():
                if pivot_col not in solution_expr:
                    continue
                
                system_expr = solution_expr[pivot_col]
                
                # 检查每个自由变量的系数
                for free_idx, coeff_entry in user_coeffs.items():
                    if free_idx == 'const':
                        continue
                    
                    try:
                        user_coeff = Fraction(coeff_entry.get().strip()).limit_denominator(10000)
                        system_coeff = system_expr['coeffs'].get(free_idx, Fraction(0))
                        
                        if user_coeff != system_coeff:
                            all_correct = False
                            break
                    except:
                        all_correct = False
                        break
                
                if not all_correct:
                    break
                
                # 检查常数项
                const_entry = user_coeffs.get('const')
                if const_entry:
                    try:
                        user_const = Fraction(const_entry.get().strip()).limit_denominator(10000)
                        system_const = system_expr['const']
                        
                        if user_const != system_const:
                            all_correct = False
                            break
                    except:
                        all_correct = False
                        break
            
            if all_correct:
                self.feedback_label.config(
                    text="✓ 太棒了！完全正确！你是数学天才！", 
                    fg="#27ae60"
                )
            else:
                self.feedback_label.config(
                    text="✗ 系数有误，正确答案如下：", 
                    fg="#e74c3c"
                )
                # 延迟1.5秒后显示解答
                self.root.after(1500, self.show_solution)
            return
        
        # 唯一解的情况（没有自由变量）
        # 获取用户输入的答案
        user_answers = []
        has_input = False
        for entry in self.answer_entries:
            value = entry.get().strip()
            if value:
                has_input = True
                try:
                    user_answers.append(Fraction(value).limit_denominator(10000))
                except:
                    self.feedback_label.config(text="✗ 答案格式错误，请输入分数或小数", fg="#e74c3c")
                    return
            else:
                user_answers.append(None)
        
        # 如果用户没有输入任何答案，直接显示解答
        if not has_input:
            self.show_solution()
            return
        
        # 检查唯一解的答案是否正确
        solution = [Fraction(0)] * m
        for i in range(rank):
            col = pivot_cols[i]
            solution[col] = augmented[i][-1]
        
        correct = True
        for i in range(m):
            if user_answers[i] is not None and user_answers[i] != solution[i]:
                correct = False
                break
        
        if correct:
            self.feedback_label.config(text="✓ 太棒了！完全正确！你是数学天才！", fg="#27ae60")
        else:
            self.feedback_label.config(text="✗ 答案有误，正确答案如下：", fg="#e74c3c")
            # 延迟1.5秒后显示解答
            self.root.after(1500, self.show_solution)
    
    def mark_no_solution(self):
        """标记方程组无解"""
        try:
            matrix, constants = self.parse_coefficients()
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return
        
        # 求解
        augmented, pivot_cols, steps = self.gauss_elimination(matrix, constants)
        n = len(matrix)
        rank = len(pivot_cols)
        
        # 检查是否真的无解
        has_contradiction = False
        if not self.is_homogeneous:
            for i in range(rank, n):
                if augmented[i][-1] != 0:
                    has_contradiction = True
                    break
        
        if has_contradiction:
            self.feedback_label.config(text="✓ 回答正确！该方程组确实无解！你太厉害了！", fg="#27ae60")
        else:
            self.feedback_label.config(text="✗ 错误！该方程组有解，点击'显示答案'查看正确解法", fg="#e74c3c")
            # 延迟1.5秒后显示解答
            self.root.after(1500, self.show_solution)
    
    def show_solution(self):
        """显示完整解答"""
        self.solve_system()
        # 不再清空feedback_label，让错误提示保留
        # self.feedback_label.config(text="", fg="#27ae60")
    
    def create_input_section(self, parent):
        """创建输入区域"""
        # 创建渐变背景容器
        input_container = tk.Frame(parent, bg="#f5f5f5")
        input_container.pack(fill="both", expand=True, pady=8)
        
        # 创建渐变Canvas（仅垂直滚动）
        canvas = tk.Canvas(input_container, bg="#f5f5f5", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(input_container, orient="vertical", command=canvas.yview)
        
        self.input_frame = tk.Frame(canvas, bg="#ffffff", padx=25, pady=12)
        
        canvas.create_window((0, 0), window=self.input_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # 布局Canvas和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        
        # 绘制渐变背景
        def draw_gradient(event=None):
            canvas.delete("gradient")
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            if width > 1 and height > 1:
                for i in range(width):
                    r = int(255 - (255 - 224) * i / width)
                    g = int(228 + (247 - 228) * i / width)
                    b = int(225 + (250 - 225) * i / width)
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    canvas.create_line(i, 0, i, height, fill=color, width=1, tags="gradient")
        
        canvas.bind("<Configure>", draw_gradient)
        
        # 更新滚动区域
        self.input_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # 绑定鼠标滚轮进行垂直滚动
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def create_solution_display(self, parent):
        """创建解题过程显示区域"""
        solution_frame = tk.Frame(parent, bg="#ffffff", padx=20, pady=15)
        solution_frame.pack(fill="both", expand=True)
        
        # 标题
        title_label = tk.Label(
            solution_frame,
            text="求解过程与结果",
            font=("Microsoft YaHei", 15, "bold"),
            fg="#2c3e50",
            bg="#f5f5f5"
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        # 滚动文本框
        text_container = tk.Frame(solution_frame, bg="#ecf0f1", relief="sunken", bd=1)
        text_container.pack(fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_container)
        scrollbar.pack(side="right", fill="y")
        
        self.solution_text = tk.Text(
            text_container,
            font=("Consolas", 13),
            bg="#ffffff",
            fg="#2c3e50",  # 深色文字，清晰可见
            relief="flat",
            bd=0,
            padx=15,
            pady=15,
            yscrollcommand=scrollbar.set,
            wrap="word",
            state="disabled",
            insertbackground="#2c3e50",
            spacing1=3,
            spacing2=3,
            spacing3=5
        )
        self.solution_text.pack(fill="both", expand=True)
        
        scrollbar.config(command=self.solution_text.yview)
    
    def create_buttons(self):
        """创建按钮区域（已整合到配置区域）"""
        # 按钮已经移到配置区域，这里不再需要创建
    
    def update_input_fields(self):
        """更新输入字段"""
        # 获取配置
        try:
            new_num_equations = int(self.eq_var.get())
            new_num_variables = int(self.var_var.get())
            new_is_homogeneous = self.homo_var.get()
        except:
            new_num_equations = 3
            new_num_variables = 3
            new_is_homogeneous = False
        
        # 检查配置是否真的改变了
        config_changed = (
            new_num_equations != self.num_equations or
            new_num_variables != self.num_variables or
            new_is_homogeneous != self.is_homogeneous
        )
        
        # 如果配置没有改变，不需要重建
        if not config_changed and self.equation_entries:
            return
        
        print(f"[DEBUG] 配置改变，重建输入框: 方程{new_num_equations}, 变量{new_num_variables}, 齐次{new_is_homogeneous}")
        
        # 更新配置
        self.num_equations = new_num_equations
        self.num_variables = new_num_variables
        self.is_homogeneous = new_is_homogeneous
        
        # 清除旧的输入字段
        for widget in self.input_frame.winfo_children():
            widget.destroy()
        
        self.equation_entries = []
        
        # 变量名列表
        var_names = ['x₁', 'x₂', 'x₃', 'x₄', 'x₅']
        
        # 清除旧的答案输入框
        for widget in self.answer_container.winfo_children():
            widget.destroy()
        
        self.answer_entries = []
        self.free_var_checkboxes = []  # 新增：自由变量复选框列表
        
        # 创建答案输入框和自由变量复选框
        for j in range(self.num_variables):
            var_frame = tk.Frame(self.answer_container, bg="#ffffff")
            var_frame.pack(side="left", padx=8, pady=5)
            
            # 变量名标签
            var_label = tk.Label(
                var_frame,
                text=f"{var_names[j]} =",
                font=("Microsoft YaHei", 12, "bold"),
                fg="#3498db",
                bg="#ffffff"
            )
            var_label.pack(side="left", padx=(0, 3))
            
            # 答案输入框
            answer_entry = tk.Entry(
                var_frame,
                font=("Arial", 13),
                bg="#ffffff",
                fg="#2c3e50",
                relief="solid",
                bd=1,
                width=10,
                justify="center"
            )
            answer_entry.pack(side="left", padx=(0, 5))
            answer_entry.insert(0, "")  # 默认为空
            self.answer_entries.append(answer_entry)
            
            # 自由变量复选框
            free_var = tk.BooleanVar(value=False)
            free_cb = tk.Checkbutton(
                var_frame,
                text="自由",
                variable=free_var,
                font=("Microsoft YaHei", 11),
                fg="#e74c3c",
                bg="#ffffff",
                selectcolor="#ffffff",
                command=lambda idx=j: self.on_free_var_change(idx)
            )
            free_cb.pack(side="left")
            self.free_var_checkboxes.append(free_var)
        
        # 创建输入行
        for i in range(self.num_equations):
            row_frame = tk.Frame(self.input_frame, bg="#ffffff")
            row_frame.pack(fill="x", pady=8)
            
            # 方程标签
            label = tk.Label(
                row_frame,
                text=f"方程 {i+1}：",
                font=("Microsoft YaHei", 13, "bold"),
                fg="#27ae60",
                bg="#ffffff"
            )
            label.pack(side="left", padx=(0, 10))
            
            # 系数输入框
            coeff_entries = []
            for j in range(self.num_variables):
                entry = tk.Entry(
                    row_frame,
                    font=("Arial", 14),
                    bg="#ffffff",
                    fg="#2c3e50",
                    relief="solid",
                    bd=1,
                    width=6,
                    justify="center"
                )
                entry.pack(side="left", padx=3)
                entry.insert(0, "0")
                coeff_entries.append(entry)
                
                # 变量名标签
                if j < len(var_names):
                    var_label = tk.Label(
                        row_frame,
                        text=var_names[j],
                        font=("Arial", 14, "bold"),
                        fg="#2c3e50",
                        bg="#ffffff"
                    )
                    var_label.pack(side="left", padx=(0, 5))
            
            if not self.is_homogeneous:
                # 非齐次方程：显示等号和常数项输入框
                equals_label = tk.Label(
                    row_frame,
                    text="=",
                    font=("Arial", 14, "bold"),
                    fg="#e74c3c",
                    bg="#ffffff"
                )
                equals_label.pack(side="left", padx=10)
                
                const_entry = tk.Entry(
                    row_frame,
                    font=("Arial", 14),
                    bg="#ffffff",
                    fg="#2c3e50",
                    relief="solid",
                    bd=1,
                    width=8,
                    justify="center"
                )
                const_entry.pack(side="left", padx=3)
                const_entry.insert(0, "0")
                
                self.equation_entries.append((coeff_entries, const_entry))
            else:
                # 齐次方程：只显示等号和红色的0，不使用输入框
                equals_label = tk.Label(
                    row_frame,
                    text="=",
                    font=("Arial", 14, "bold"),
                    fg="#e74c3c",
                    bg="#ffffff"
                )
                equals_label.pack(side="left", padx=10)
                
                # 显示红色的0
                zero_label = tk.Label(
                    row_frame,
                    text="0",
                    font=("Arial", 14, "bold"),
                    fg="#e74c3c",  # 红色字体
                    bg="#ffffff"
                )
                zero_label.pack(side="left", padx=3)
                
                # 创建一个隐藏的Entry用于存储值（始终为0）
                const_entry = tk.Entry(
                    row_frame,
                    font=("Arial", 12),
                    bg="#ffffff",
                    fg="#2c3e50",
                    relief="solid",
                    bd=1,
                    width=8,
                    justify="center"
                )
                const_entry.pack_forget()  # 隐藏
                const_entry.delete(0, tk.END)
                const_entry.insert(0, "0")
                
                self.equation_entries.append((coeff_entries, const_entry))
        
        print(f"[DEBUG] 创建了 {len(self.equation_entries)} 个方程输入框")
        
        # 强制更新界面
        self.input_frame.update_idletasks()
        self.root.update()
    
    def parse_coefficients(self):
        """解析系数矩阵和常数向量"""
        matrix = []
        constants = []
        
        for entry_data in self.equation_entries:
            coeff_entries = entry_data[0]
            const_entry = entry_data[1]
            
            row = []
            for entry in coeff_entries:
                try:
                    value = float(entry.get())
                    row.append(value)
                except:
                    raise ValueError("系数必须为数字")
            
            if const_entry is not None:
                try:
                    const_value = float(const_entry.get())
                except:
                    raise ValueError("常数项必须为数字")
            else:
                const_value = 0.0
            
            matrix.append(row)
            constants.append(const_value)
        
        return matrix, constants
    
    def fraction_to_string(self, value):
        """将数值转换为最简分数或整数形式"""
        if isinstance(value, Fraction):
            frac = value
        else:
            frac = Fraction(value).limit_denominator(10000)
        
        if frac.denominator == 1:
            return str(frac.numerator)
        else:
            return f"{frac.numerator}/{frac.denominator}"
    
    def gauss_elimination(self, matrix, constants):
        """高斯消元法求解线性方程组"""
        n = len(matrix)
        m = len(matrix[0]) if n > 0 else 0
        
        # 创建增广矩阵
        augmented = []
        for i in range(n):
            row = [Fraction(str(matrix[i][j])).limit_denominator(10000) for j in range(m)]
            row.append(Fraction(str(constants[i])).limit_denominator(10000))
            augmented.append(row)
        
        steps = []
        steps.append("增广矩阵 [A|b]：")
        steps.append(self.matrix_to_string(augmented))
        steps.append("")
        
        # 前向消元
        pivot_row = 0
        pivot_cols = []
        
        for col in range(m):
            if pivot_row >= n:
                break
            
            # 寻找主元
            max_row = pivot_row
            for row in range(pivot_row + 1, n):
                if abs(augmented[row][col]) > abs(augmented[max_row][col]):
                    max_row = row
            
            # 如果主元为0，跳过此列
            if augmented[max_row][col] == 0:
                continue
            
            # 交换行
            if max_row != pivot_row:
                augmented[pivot_row], augmented[max_row] = augmented[max_row], augmented[pivot_row]
                steps.append(f"交换行 {pivot_row + 1} ↔ 行 {max_row + 1}：")
                steps.append(self.matrix_to_string(augmented))
                steps.append("")
            
            pivot_cols.append(col)
            
            # 归一化主元行
            pivot_val = augmented[pivot_row][col]
            for j in range(len(augmented[pivot_row])):
                augmented[pivot_row][j] /= pivot_val
            
            steps.append(f"行 {pivot_row + 1} ÷ ({self.fraction_to_string(pivot_val)})：")
            steps.append(self.matrix_to_string(augmented))
            steps.append("")
            
            # 消去其他行的该列
            for row in range(n):
                if row != pivot_row and augmented[row][col] != 0:
                    factor = augmented[row][col]
                    for j in range(len(augmented[row])):
                        augmented[row][j] -= factor * augmented[pivot_row][j]
                    
                    steps.append(f"行 {row + 1} - ({self.fraction_to_string(factor)}) × 行 {pivot_row + 1}：")
                    steps.append(self.matrix_to_string(augmented))
                    steps.append("")
            
            pivot_row += 1
        
        return augmented, pivot_cols, steps
    
    def matrix_to_string(self, matrix):
        """将矩阵转换为字符串"""
        lines = []
        for row in matrix:
            line = "│ "
            for val in row:
                line += f"{self.fraction_to_string(val):>8} "
            line += "│"
            lines.append(line)
        return "\n".join(lines)
    
    def solve_system(self):
        """求解线性方程组"""
        try:
            print("[DEBUG] 开始求解...")
            print(f"[DEBUG] equation_entries数量: {len(self.equation_entries)}")
            
            if not self.equation_entries:
                messagebox.showwarning("提示", "请先点击'应用配置'按钮生成输入框！")
                return
            
            # 解析系数
            matrix, constants = self.parse_coefficients()
            print(f"[DEBUG] 解析完成: {len(matrix)}个方程, {len(matrix[0])}个变量")
            print(f"[DEBUG] 矩阵: {matrix}")
            print(f"[DEBUG] 常数: {constants}")
            
            steps = []
            steps.append("=" * 75)
            
            if self.is_homogeneous:
                steps.append("齐次线性方程组求解过程")
            else:
                steps.append("非齐次线性方程组求解过程")
            
            steps.append("=" * 75)
            steps.append("")
            
            # 显示原方程组
            var_names = ['x₁', 'x₂', 'x₃', 'x₄', 'x₅']
            steps.append("原方程组：")
            for i in range(len(matrix)):
                eq_str = ""
                for j in range(len(matrix[i])):
                    coeff = matrix[i][j]
                    if coeff != 0:
                        if eq_str:
                            eq_str += " + " if coeff > 0 else " - "
                        elif coeff < 0:
                            eq_str += "-"
                        
                        abs_coeff = abs(coeff)
                        if abs_coeff != 1:
                            eq_str += self.fraction_to_string(abs_coeff)
                        
                        if j < len(var_names):
                            eq_str += var_names[j]
                
                if not eq_str:
                    eq_str = "0"
                
                if self.is_homogeneous:
                    eq_str += " = 0"
                else:
                    eq_str += f" = {self.fraction_to_string(constants[i])}"
                
                steps.append(f"  ({i+1}) {eq_str}")
            steps.append("")
            
            # 高斯消元
            augmented, pivot_cols, elim_steps = self.gauss_elimination(matrix, constants)
            steps.extend(elim_steps)
            
            # 分析结果
            n = len(matrix)
            m = len(matrix[0])
            rank = len(pivot_cols)
            
            steps.append("=" * 75)
            steps.append("结果分析")
            steps.append("=" * 75)
            steps.append("")
            steps.append(f"系数矩阵的秩 r(A) = {rank}")
            steps.append(f"增广矩阵的秩 r(A|b) = {rank}")
            steps.append(f"未知量个数 n = {m}")
            steps.append(f"方程个数 = {n}")
            steps.append("")
            
            if self.is_homogeneous:
                # 齐次方程组的解
                self.analyze_homogeneous_solution(steps, augmented, pivot_cols, rank, m, var_names)
            else:
                # 非齐次方程组的解
                self.analyze_nonhomogeneous_solution(steps, augmented, pivot_cols, rank, n, m, var_names)
            
            steps.append("")
            steps.append("=" * 75)
            
            result_text = "\n".join(steps)
            print(f"[DEBUG] 结果文本长度: {len(result_text)}")
            print(f"[DEBUG] 准备显示结果...")
            self.display_solution(result_text)
            print(f"[DEBUG] 结果显示完成！")
            
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            messagebox.showerror("求解错误", f"求解过程中出错：{str(e)}")
            import traceback
            traceback.print_exc()
    
    def analyze_homogeneous_solution(self, steps, augmented, pivot_cols, rank, m, var_names):
        """分析齐次方程组的解"""
        num_free_vars = m - rank
        
        if num_free_vars == 0:
            steps.append("✓ 齐次方程组只有零解（唯一解）")
            steps.append("")
            steps.append("解为：")
            for j in range(m):
                if j < len(var_names):
                    steps.append(f"  {var_names[j]} = 0")
        else:
            steps.append(f"⚠ 齐次方程组有无穷多解（非零解）")
            steps.append(f"自由变量个数 = n - r(A) = {m} - {rank} = {num_free_vars}")
            steps.append("")
            
            # 找出自由变量
            free_vars = []
            for j in range(m):
                if j not in pivot_cols:
                    free_vars.append(j)
            
            steps.append("自由变量：")
            for idx in free_vars:
                if idx < len(var_names):
                    steps.append(f"  {var_names[idx]} (可取任意值)")
            steps.append("")
            
            # 表达主变量
            steps.append("基础解系（通解）：")
            for i in range(rank):
                col = pivot_cols[i]
                var_name = var_names[col] if col < len(var_names) else f"x{col+1}"
                
                expr = "0"
                for j in free_vars:
                    coeff = -augmented[i][j]
                    if coeff != 0:
                        free_var_name = var_names[j] if j < len(var_names) else f"x{j+1}"
                        if coeff == 1:
                            expr += f" + {free_var_name}" if expr != "0" else free_var_name
                        elif coeff == -1:
                            expr += f" - {free_var_name}"
                        elif coeff > 0:
                            expr += f" + {self.fraction_to_string(coeff)}{free_var_name}" if expr != "0" else f"{self.fraction_to_string(coeff)}{free_var_name}"
                        else:
                            expr += f" - {self.fraction_to_string(abs(coeff))}{free_var_name}"
                
                if expr == "0":
                    expr = "0"
                
                steps.append(f"  {var_name} = {expr}")
            
            # 自由变量本身
            for idx in free_vars:
                var_name = var_names[idx] if idx < len(var_names) else f"x{idx+1}"
                steps.append(f"  {var_name} = {var_name} (自由变量)")
            
            steps.append("")
            steps.append("说明：令自由变量取不同的值，可得到不同的解向量")
    
    def analyze_nonhomogeneous_solution(self, steps, augmented, pivot_cols, rank, n, m, var_names):
        """分析非齐次方程组的解"""
        # 检查是否有矛盾（无解）
        has_contradiction = False
        for i in range(rank, n):
            if augmented[i][-1] != 0:
                has_contradiction = True
                break
        
        if has_contradiction:
            steps.append("✗ 非齐次方程组无解！")
            steps.append("")
            steps.append("原因：增广矩阵的秩 r(A|b) > 系数矩阵的秩 r(A)")
            steps.append("存在矛盾方程（如 0 = 非零值）")
        else:
            num_free_vars = m - rank
            
            if num_free_vars == 0:
                # 唯一解
                steps.append("✓ 非齐次方程组有唯一解")
                steps.append("")
                steps.append("解为：")
                
                solution = [Fraction(0)] * m
                for i in range(rank):
                    col = pivot_cols[i]
                    solution[col] = augmented[i][-1]
                
                for j in range(m):
                    if j < len(var_names):
                        steps.append(f"  {var_names[j]} = {self.fraction_to_string(solution[j])}")
                
            elif num_free_vars > 0:
                # 无穷多解
                steps.append(f"⚠ 非齐次方程组有无穷多解")
                steps.append(f"自由变量个数 = n - r(A) = {m} - {rank} = {num_free_vars}")
                steps.append("")
                
                # 找出自由变量
                free_vars = []
                for j in range(m):
                    if j not in pivot_cols:
                        free_vars.append(j)
                
                steps.append("自由变量：")
                for idx in free_vars:
                    if idx < len(var_names):
                        steps.append(f"  {var_names[idx]} (可取任意值)")
                steps.append("")
                
                # 表达主变量
                steps.append("通解（特解 + 齐次通解）：")
                for i in range(rank):
                    col = pivot_cols[i]
                    var_name = var_names[col] if col < len(var_names) else f"x{col+1}"
                    
                    expr = self.fraction_to_string(augmented[i][-1])
                    
                    for j in free_vars:
                        coeff = -augmented[i][j]
                        if coeff != 0:
                            free_var_name = var_names[j] if j < len(var_names) else f"x{j+1}"
                            if coeff == 1:
                                expr += f" + {free_var_name}"
                            elif coeff == -1:
                                expr += f" - {free_var_name}"
                            elif coeff > 0:
                                expr += f" + {self.fraction_to_string(coeff)}{free_var_name}"
                            else:
                                expr += f" - {self.fraction_to_string(abs(coeff))}{free_var_name}"
                    
                    steps.append(f"  {var_name} = {expr}")
                
                # 自由变量本身
                for idx in free_vars:
                    var_name = var_names[idx] if idx < len(var_names) else f"x{idx+1}"
                    steps.append(f"  {var_name} = {var_name} (自由变量)")
    
    def display_solution(self, text):
        """显示解题过程"""
        print(f"[DEBUG] 进入display_solution函数")
        print(f"[DEBUG] solution_text状态: {self.solution_text.cget('state')}")
        
        self.solution_text.config(state="normal")
        print(f"[DEBUG] 已设置为normal状态")
        
        self.solution_text.delete(1.0, tk.END)
        print(f"[DEBUG] 已清空文本框")
        
        self.solution_text.insert(tk.END, text)
        print(f"[DEBUG] 已插入文本")
        
        self.solution_text.config(state="disabled")
        print(f"[DEBUG] 已设置为disabled状态")
        
        # 强制刷新界面
        self.root.update_idletasks()
        self.root.update()
        print(f"[DEBUG] 界面刷新完成")
    
    def clear_all(self):
        """清空所有内容"""
        self.homo_var.set(False)
        self.eq_var.set("3")
        self.var_var.set("3")
        self.is_homogeneous = False
        self.update_input_fields()
        
        self.solution_text.config(state="normal")
        self.solution_text.delete(1.0, tk.END)
        self.solution_text.config(state="disabled")
        
        # 清除反馈标签
        self.feedback_label.config(text="", fg="#27ae60")
    
    def load_example(self):
        """加载示例"""
        # 设置为非齐次方程，3个方程3个变量
        self.homo_var.set(False)
        self.eq_var.set("3")
        self.var_var.set("3")
        self.is_homogeneous = False
        self.update_input_fields()
        
        # 清除反馈标签
        self.feedback_label.config(text="", fg="#27ae60")
        
        # 等待界面更新后填充数据
        self.root.after(200, self._fill_example_data)
    
    def _fill_example_data(self):
        """填充示例数据"""
        # 示例：非齐次方程组有唯一解
        # x₁ + x₂ + x₃ = 6
        # 2x₁ - x₂ + x₃ = 3
        # x₁ + 2x₂ - x₃ = 2
        
        examples = [
            ([1, 1, 1], 6),
            ([2, -1, 1], 3),
            ([1, 2, -1], 2)
        ]
        
        for i, (coeffs, const) in enumerate(examples):
            if i < len(self.equation_entries):
                coeff_entries = self.equation_entries[i][0]
                const_entry = self.equation_entries[i][1]
                for j, val in enumerate(coeffs):
                    coeff_entries[j].delete(0, tk.END)
                    coeff_entries[j].insert(0, str(val))
                if const_entry:
                    const_entry.delete(0, tk.END)
                    const_entry.insert(0, str(const))
        
        # 自动求解
        self.root.after(100, self.solve_system)
    
    def show_contact_info(self):
        """显示开发者联系信息"""
        contact_message = """感谢您参加本次程序测试
如遇到程序bug或计算错误的情况，请联系开发者：

北京建筑大学
测绘与城市空间信息学院
遥感实验252
李牧义
15601022293"""
        messagebox.showinfo("联系开发者", contact_message)


def main():
    """主函数"""
    root = tk.Tk()
    app = LinearEquationSolver(root)
    root.mainloop()


if __name__ == "__main__":
    main()