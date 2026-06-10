import streamlit as st
from fractions import Fraction
import pandas as pd


def fraction_to_string(value):
    """将数值转换为最简分数或整数形式"""
    if isinstance(value, Fraction):
        frac = value
    else:
        frac = Fraction(value).limit_denominator(10000)
    
    if frac.denominator == 1:
        return str(frac.numerator)
    else:
        return f"{frac.numerator}/{frac.denominator}"


def gauss_elimination(matrix, constants):
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
    steps.append(matrix_to_string(augmented))
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
            steps.append(matrix_to_string(augmented))
            steps.append("")
        
        pivot_cols.append(col)
        
        # 归一化主元行
        pivot_val = augmented[pivot_row][col]
        for j in range(len(augmented[pivot_row])):
            augmented[pivot_row][j] /= pivot_val
        
        steps.append(f"行 {pivot_row + 1} ÷ ({fraction_to_string(pivot_val)})：")
        steps.append(matrix_to_string(augmented))
        steps.append("")
        
        # 消去其他行的该列
        for row in range(n):
            if row != pivot_row and augmented[row][col] != 0:
                factor = augmented[row][col]
                for j in range(len(augmented[row])):
                    augmented[row][j] -= factor * augmented[pivot_row][j]
                
                steps.append(f"行 {row + 1} - ({fraction_to_string(factor)}) × 行 {pivot_row + 1}：")
                steps.append(matrix_to_string(augmented))
                steps.append("")
        
        pivot_row += 1
    
    return augmented, pivot_cols, steps


def matrix_to_string(matrix):
    """将矩阵转换为字符串"""
    lines = []
    for row in matrix:
        line = "│ "
        for val in row:
            line += f"{fraction_to_string(val):>8} "
        line += "│"
        lines.append(line)
    return "\n".join(lines)


def solve_system(equations_data, is_homogeneous):
    """求解线性方程组"""
    var_names = ['x₁', 'x₂', 'x₃', 'x₄', 'x₅']
    
    # 解析数据
    matrix = []
    constants = []
    for eq_data in equations_data:
        matrix.append(eq_data['coeffs'])
        constants.append(eq_data['const'])
    
    steps = []
    steps.append("=" * 75)
    
    if is_homogeneous:
        steps.append("齐次线性方程组求解过程")
    else:
        steps.append("非齐次线性方程组求解过程")
    
    steps.append("=" * 75)
    steps.append("")
    
    # 显示原方程组
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
                    eq_str += fraction_to_string(abs_coeff)
                
                if j < len(var_names):
                    eq_str += var_names[j]
        
        if not eq_str:
            eq_str = "0"
        
        if is_homogeneous:
            eq_str += " = 0"
        else:
            eq_str += f" = {fraction_to_string(constants[i])}"
        
        steps.append(f"  ({i+1}) {eq_str}")
    steps.append("")
    
    # 高斯消元
    augmented, pivot_cols, elim_steps = gauss_elimination(matrix, constants)
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
    
    if is_homogeneous:
        analyze_homogeneous_solution(steps, augmented, pivot_cols, rank, m, var_names)
    else:
        analyze_nonhomogeneous_solution(steps, augmented, pivot_cols, rank, n, m, var_names)
    
    steps.append("")
    steps.append("=" * 75)
    
    return "\n".join(steps), augmented, pivot_cols, rank, m


def analyze_homogeneous_solution(steps, augmented, pivot_cols, rank, m, var_names):
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
                        expr += f" + {fraction_to_string(coeff)}{free_var_name}" if expr != "0" else f"{fraction_to_string(coeff)}{free_var_name}"
                    else:
                        expr += f" - {fraction_to_string(abs(coeff))}{free_var_name}"
            
            if expr == "0":
                expr = "0"
            
            steps.append(f"  {var_name} = {expr}")
        
        # 自由变量本身
        for idx in free_vars:
            var_name = var_names[idx] if idx < len(var_names) else f"x{idx+1}"
            steps.append(f"  {var_name} = {var_name} (自由变量)")
        
        steps.append("")
        steps.append("说明：令自由变量取不同的值，可得到不同的解向量")


def analyze_nonhomogeneous_solution(steps, augmented, pivot_cols, rank, n, m, var_names):
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
                    steps.append(f"  {var_names[j]} = {fraction_to_string(solution[j])}")
            
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
                
                expr = fraction_to_string(augmented[i][-1])
                
                for j in free_vars:
                    coeff = -augmented[i][j]
                    if coeff != 0:
                        free_var_name = var_names[j] if j < len(var_names) else f"x{j+1}"
                        if coeff == 1:
                            expr += f" + {free_var_name}"
                        elif coeff == -1:
                            expr += f" - {free_var_name}"
                        elif coeff > 0:
                            expr += f" + {fraction_to_string(coeff)}{free_var_name}"
                        else:
                            expr += f" - {fraction_to_string(abs(coeff))}{free_var_name}"
                
                steps.append(f"  {var_name} = {expr}")
            
            # 自由变量本身
            for idx in free_vars:
                var_name = var_names[idx] if idx < len(var_names) else f"x{idx+1}"
                steps.append(f"  {var_name} = {var_name} (自由变量)")


# Streamlit应用主界面
st.set_page_config(page_title="线性方程组求解器", page_icon="🧮", layout="wide")

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(to right, #FFE4E1, #E0F7FA);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# 标题区域
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🧮 线性方程组求解器")
st.markdown("支持齐次/非齐次线性方程组 · 自动检测自由变量 · 最简分数形式")
if st.button("📞 联系开发者", key="contact_btn"):
    st.info("""
    **感谢您参加本次程序测试**
    
    如遇到程序bug或计算错误的情况，请联系开发者：
    
    **北京建筑大学**  
    测绘与城市空间信息学院  
    遥感实验252  
    **李牧义**  
    📱 15601022293
    """)
st.markdown('</div>', unsafe_allow_html=True)

# 配置区域
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    is_homogeneous = st.checkbox("齐次方程组 (Ax=0)", value=False)

with col2:
    num_equations = st.selectbox("方程数量", [1, 2, 3, 4, 5], index=2)

with col3:
    num_variables = st.selectbox("未知量个数", [1, 2, 3, 4, 5], index=2)

# 清空和加载示例按钮
col_clear, col_example = st.columns(2)
with col_clear:
    if st.button("️ 清空重置", use_container_width=True):
        st.session_state.clear()
        st.rerun()

with col_example:
    if st.button("📋 加载示例", use_container_width=True):
        # 设置默认值
        st.session_state['example_loaded'] = True
        st.rerun()

# 初始化session state
if 'equations_data' not in st.session_state:
    st.session_state.equations_data = []

# 加载示例数据
if st.session_state.get('example_loaded', False):
    example_data = [
        {'coeffs': [1, 1, 1], 'const': 6},
        {'coeffs': [2, -1, 1], 'const': 3},
        {'coeffs': [1, 2, -1], 'const': 2}
    ]
    st.session_state.equations_data = example_data
    st.session_state.example_loaded = False

# 方程输入区域
st.subheader("📝 请输入方程组系数")

equations_data = []
var_names = ['x₁', 'x₂', 'x₃', 'x₄', 'x₅']

for i in range(num_equations):
    st.markdown(f"**方程 {i+1}:**")
    cols = st.columns(num_variables + 1)
    
    coeffs = []
    for j in range(num_variables):
        key = f"eq_{i}_var_{j}"
        # 如果有示例数据，使用示例值
        default_value = 0
        if st.session_state.get('equations_data') and i < len(st.session_state.equations_data):
            if j < len(st.session_state.equations_data[i]['coeffs']):
                default_value = st.session_state.equations_data[i]['coeffs'][j]
        
        coeff = cols[j].number_input(
            f"{var_names[j]} 系数",
            value=float(default_value),
            step=1.0,
            format="%.2f",
            key=key
        )
        coeffs.append(coeff)
    
    # 常数项（非齐次方程）
    const_key = f"eq_{i}_const"
    default_const = 0
    if st.session_state.get('equations_data') and i < len(st.session_state.equations_data):
        default_const = st.session_state.equations_data[i]['const']
    
    if not is_homogeneous:
        const = cols[-1].number_input(
            "常数项",
            value=float(default_const),
            step=1.0,
            format="%.2f",
            key=const_key
        )
    else:
        cols[-1].markdown("**= 0**")
        const = 0.0
    
    equations_data.append({
        'coeffs': coeffs,
        'const': const
    })

# 保存当前数据到session state
st.session_state.equations_data = equations_data

# 用户答案输入区域
st.markdown("---")
st.subheader("✍️ 请输入你的答案（可选，留空直接看解答）")

# 初始化答案相关session state
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'free_vars_selected' not in st.session_state:
    st.session_state.free_vars_selected = []
if 'feedback_message' not in st.session_state:
    st.session_state.feedback_message = ""
if 'feedback_color' not in st.session_state:
    st.session_state.feedback_color = ""

# 创建答案输入框
answer_cols = st.columns(num_variables)
user_answers = {}
for j in range(num_variables):
    var_key = f"answer_var_{j}"
    answer = answer_cols[j].text_input(
        f"{var_names[j]} =",
        value=st.session_state.user_answers.get(j, ""),
        key=var_key,
        placeholder="输入分数或小数"
    )
    user_answers[j] = answer.strip()

# 自由变量复选框
st.markdown("**勾选自由变量：**")
free_var_cols = st.columns(num_variables)
free_vars_selected = []
for j in range(num_variables):
    free_key = f"free_var_{j}"
    is_free = free_var_cols[j].checkbox(
        f"{var_names[j]} 是自由变量",
        value=j in st.session_state.free_vars_selected,
        key=free_key
    )
    if is_free:
        free_vars_selected.append(j)

# 系数输入框（当有自由变量时显示）
coefficient_entries = {}
if free_vars_selected:
    st.markdown("**请输入各主元变量的系数表达式：**")
    
    # 找出非自由变量（主元变量）
    pivot_vars = [j for j in range(num_variables) if j not in free_vars_selected]
    
    for pivot_idx in pivot_vars:
        st.markdown(f"\n**{var_names[pivot_idx]} = **")
        coeff_cols = st.columns(len(free_vars_selected) + 1)
        
        coefficient_entries[pivot_idx] = {}
        
        # 每个自由变量的系数
        for i, free_idx in enumerate(free_vars_selected):
            coeff_key = f"coeff_{pivot_idx}_{free_idx}"
            coeff_value = coeff_cols[i].number_input(
                f"{var_names[free_idx]} 的系数",
                value=0.0,
                step=1.0,
                format="%.2f",
                key=coeff_key
            )
            coefficient_entries[pivot_idx][free_idx] = coeff_value
        
        # 常数项
        const_key = f"const_{pivot_idx}"
        const_value = coeff_cols[-1].number_input(
            "常数项",
            value=0.0,
            step=1.0,
            format="%.2f",
            key=const_key
        )
        coefficient_entries[pivot_idx]['const'] = const_value

# 提交答案、显示答案、无解按钮
col_submit, col_show, col_no_solution = st.columns(3)

with col_submit:
    if st.button("✅ 提交答案", type="primary", use_container_width=True):
        # 检查是否有解的结果
        if 'solution_result' not in st.session_state:
            st.warning("请先点击'求解方程组'按钮！")
        else:
            # 获取之前求解的结果
            try:
                matrix = []
                constants = []
                for eq_data in equations_data:
                    matrix.append(eq_data['coeffs'])
                    constants.append(eq_data['const'])
                
                augmented, pivot_cols, steps = gauss_elimination(matrix, constants)
                n = len(matrix)
                m = len(matrix[0])
                rank = len(pivot_cols)
                
                # 检查是否有解
                has_contradiction = False
                if not is_homogeneous:
                    for i in range(rank, n):
                        if augmented[i][-1] != 0:
                            has_contradiction = True
                            break
                
                # 如果无解
                if has_contradiction:
                    st.session_state.feedback_message = "❌ 答案错误！该方程组无解，请点击'无解'按钮"
                    st.session_state.feedback_color = "error"
                else:
                    # 检查自由变量标记
                    num_free_vars = m - rank
                    system_free_vars = [j for j in range(m) if j not in pivot_cols]
                    
                    if num_free_vars > 0:
                        # 有自由变量的情况
                        if set(free_vars_selected) != set(system_free_vars):
                            if len(free_vars_selected) == 0:
                                st.session_state.feedback_message = "⚠️ 方程组有无穷多解，请勾选自由变量"
                                st.session_state.feedback_color = "warning"
                            else:
                                st.session_state.feedback_message = "❌ 自由变量标记有误，正确答案如下："
                                st.session_state.feedback_color = "error"
                        else:
                            # 用户正确标记了自由变量，检查系数
                            if not coefficient_entries:
                                st.session_state.feedback_message = "✅ 太棒了！你正确识别了自由变量！点击查看完整通解"
                                st.session_state.feedback_color = "success"
                            else:
                                # 构建系统的通解表达式
                                solution_expr = {}
                                for i in range(rank):
                                    pivot_col = pivot_cols[i]
                                    expr = {'const': augmented[i][-1], 'coeffs': {}}
                                    for free_idx in system_free_vars:
                                        expr['coeffs'][free_idx] = -augmented[i][free_idx]
                                    solution_expr[pivot_col] = expr
                                
                                # 检查用户输入的系数
                                all_correct = True
                                for pivot_col, user_coeffs in coefficient_entries.items():
                                    if pivot_col not in solution_expr:
                                        continue
                                    
                                    system_expr = solution_expr[pivot_col]
                                    
                                    # 检查每个自由变量的系数
                                    for free_idx, user_coeff in user_coeffs.items():
                                        if free_idx == 'const':
                                            continue
                                        
                                        try:
                                            user_coeff_frac = Fraction(str(user_coeff)).limit_denominator(10000)
                                            system_coeff = system_expr['coeffs'].get(free_idx, Fraction(0))
                                            
                                            if user_coeff_frac != system_coeff:
                                                all_correct = False
                                                break
                                        except:
                                            all_correct = False
                                            break
                                    
                                    if not all_correct:
                                        break
                                    
                                    # 检查常数项
                                    const_entry = user_coeffs.get('const')
                                    if const_entry is not None:
                                        try:
                                            user_const = Fraction(str(const_entry)).limit_denominator(10000)
                                            system_const = system_expr['const']
                                            
                                            if user_const != system_const:
                                                all_correct = False
                                                break
                                        except:
                                            all_correct = False
                                            break
                                
                                if all_correct:
                                    st.session_state.feedback_message = " 太棒了！完全正确！你是数学天才！"
                                    st.session_state.feedback_color = "success"
                                else:
                                    st.session_state.feedback_message = "❌ 系数有误，正确答案如下："
                                    st.session_state.feedback_color = "error"
                    else:
                        # 唯一解的情况
                        has_input = any(v.strip() for v in user_answers.values())
                        
                        if not has_input:
                            st.session_state.feedback_message = " 您未输入答案，将直接显示解答"
                            st.session_state.feedback_color = "info"
                        else:
                            # 检查唯一解的答案
                            solution = [Fraction(0)] * m
                            for i in range(rank):
                                col = pivot_cols[i]
                                solution[col] = augmented[i][-1]
                            
                            correct = True
                            for i in range(m):
                                if user_answers.get(i, '').strip():
                                    try:
                                        user_val = Fraction(user_answers[i]).limit_denominator(10000)
                                        if user_val != solution[i]:
                                            correct = False
                                            break
                                    except:
                                        correct = False
                                        break
                            
                            if correct:
                                st.session_state.feedback_message = " 太棒了！完全正确！你是数学天才！"
                                st.session_state.feedback_color = "success"
                            else:
                                st.session_state.feedback_message = "❌ 答案有误，正确答案如下："
                                st.session_state.feedback_color = "error"
                
                # 保存用户输入
                st.session_state.user_answers = user_answers
                st.session_state.free_vars_selected = free_vars_selected
                
            except Exception as e:
                st.session_state.feedback_message = f"❌ 验证过程中出错：{str(e)}"
                st.session_state.feedback_color = "error"

with col_show:
    if st.button("📖 显示答案", use_container_width=True):
        if 'solution_result' in st.session_state:
            st.session_state.show_solution = True
            st.session_state.feedback_message = ""
            st.session_state.feedback_color = ""
        else:
            st.warning("请先点击'求解方程组'按钮")

with col_no_solution:
    if st.button("❌ 无解", use_container_width=True):
        if 'solution_result' not in st.session_state:
            st.warning("请先点击'求解方程组'按钮！")
        else:
            # 检查是否真的无解
            try:
                matrix = []
                constants = []
                for eq_data in equations_data:
                    matrix.append(eq_data['coeffs'])
                    constants.append(eq_data['const'])
                
                augmented, pivot_cols, steps = gauss_elimination(matrix, constants)
                n = len(matrix)
                rank = len(pivot_cols)
                
                has_contradiction = False
                if not is_homogeneous:
                    for i in range(rank, n):
                        if augmented[i][-1] != 0:
                            has_contradiction = True
                            break
                
                if has_contradiction:
                    st.session_state.feedback_message = "✅ 回答正确！该方程组确实无解！你太厉害了！"
                    st.session_state.feedback_color = "success"
                else:
                    st.session_state.feedback_message = "❌ 错误！该方程组有解，点击'显示答案'查看正确解法"
                    st.session_state.feedback_color = "error"
                    st.session_state.show_solution = True
                    
            except Exception as e:
                st.session_state.feedback_message = f"❌ 验证过程中出错：{str(e)}"
                st.session_state.feedback_color = "error"

# 显示反馈消息
if st.session_state.feedback_message:
    if st.session_state.feedback_color == "success":
        st.success(st.session_state.feedback_message)
    elif st.session_state.feedback_color == "error":
        st.error(st.session_state.feedback_message)
    elif st.session_state.feedback_color == "warning":
        st.warning(st.session_state.feedback_message)
    elif st.session_state.feedback_color == "info":
        st.info(st.session_state.feedback_message)

# 求解按钮
st.markdown("---")
col_solve, col_show = st.columns(2)

with col_solve:
    if st.button("🔍 求解方程组", type="primary", use_container_width=True):
        try:
            result_text, augmented, pivot_cols, rank, m = solve_system(equations_data, is_homogeneous)
            st.session_state.solution_result = result_text
            st.session_state.has_solution = True
            
            # 检查是否有解
            has_contradiction = False
            if not is_homogeneous:
                n = len(equations_data)
                for i in range(rank, n):
                    if augmented[i][-1] != 0:
                        has_contradiction = True
                        break
            
            st.session_state.is_no_solution = has_contradiction
            
        except Exception as e:
            st.error(f"求解过程中出错：{str(e)}")
            import traceback
            st.error(traceback.format_exc())

with col_show:
    if st.button("📖 显示解答", use_container_width=True):
        if 'solution_result' in st.session_state:
            st.session_state.show_solution = True
        else:
            st.warning("请先点击'求解方程组'按钮")

# 显示解答结果
if st.session_state.get('has_solution', False):
    st.markdown("---")
    st.subheader("📊 求解过程与结果")
    
    if st.session_state.get('show_solution', False) or st.session_state.get('is_no_solution', False):
        st.code(st.session_state.solution_result, language=None)
        
        # 如果是无解的情况，特别提示
        if st.session_state.get('is_no_solution', False):
            st.error("⚠️ 该方程组无解！")
    else:
        st.info("点击上方'显示解答'按钮查看详细求解过程")

# 页脚
st.markdown("---")
st.markdown("*Made with ❤️ by 李牧义 | 北京建筑大学 测绘与城市空间信息学院*")
