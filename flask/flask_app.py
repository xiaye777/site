import os
import string
import random
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)
CODES_FILE = 'codes.txt'


def generate_random_code(length=10):
    """生成指定长度的随机字符串，包含数字和小写字母"""
    characters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(characters) for i in range(length))


def generate_codes_file():
    """生成100个唯一的随机码并保存到文件中"""
    codes = set()
    while len(codes) < 100:
        code = generate_random_code()
        codes.add(code)

    with open(CODES_FILE, 'w') as f:
        for code in codes:
            f.write(f"{code} 0\n")


def read_codes_dict():
    """从文件中读取代码字典"""
    if not os.path.exists(CODES_FILE):
        generate_codes_file()

    codes_dict = {}
    with open(CODES_FILE, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                code, status = parts[0], parts[1]
                codes_dict[code] = status
    return codes_dict


def save_codes_dict(codes_dict):
    """将代码字典保存到文件中"""
    with open(CODES_FILE, 'w') as f:
        for code, status in codes_dict.items():
            f.write(f"{code} {status}\n")


@app.route('/codes')
def generate_codes():
    """生成随机码并显示在HTML表格中"""
    generate_codes_file()
    codes_dict = read_codes_dict()
    codes = list(codes_dict.keys())

    # 将100个代码分成20行5列
    table_data = []
    for i in range(0, 100, 5):
        table_data.append(codes[i:i + 5])

    # 使用简单的HTML模板显示表格
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>考勤码列表</title>
        <style>
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <h1>考勤码列表</h1>
        <table>
            <thead>
                <tr>
                    <th>代码1</th>
                    <th>代码2</th>
                    <th>代码3</th>
                    <th>代码4</th>
                    <th>代码5</th>
                </tr>
            </thead>
            <tbody>
                {% for row in table_data %}
                <tr>
                    {% for code in row %}
                    <td>{{ code }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """

    return render_template_string(html_template, table_data=table_data)


@app.route('/signin')
def sign_in_form():
    """显示签到表单"""
    html_form = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>考勤签到</title>
    </head>
    <body>
        <h1>考勤签到</h1>
        <form method="post" action="/verify">
            <div>
                <label for="sid">学号:</label>
                <input type="text" id="sid" name="sid" required>
            </div>
            <div>
                <label for="code">签到码:</label>
                <input type="text" id="code" name="code" required>
            </div>
            <button type="submit">签到</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(html_form)


@app.route('/verify', methods=['GET', 'POST'])
def verify_code():
    """验证签到码"""
    # 获取参数
    if request.method == 'POST':
        sid = request.form.get('sid')
        code = request.form.get('code')
    else:  # GET方法
        sid = request.args.get('sid')
        code = request.args.get('code')

    # 验证参数
    if not sid or not code:
        return "错误: 缺少学号或签到码", 400

    # 读取代码字典
    codes_dict = read_codes_dict()

    # 验证代码
    if code not in codes_dict:
        return "错误: 输入的签到码不正确"

    signed_sid = codes_dict[code]

    if signed_sid == '0':
        # 代码未被使用，更新为当前学生ID
        codes_dict[code] = sid
        save_codes_dict(codes_dict)
        return "签到成功"
    elif signed_sid == sid:
        return "你已经签到过了"
    else:
        return f"该签到码已被 {signed_sid} 使用，不能共享"


@app.route('/attended')
def get_attended_students():
    """获取已签到的学生列表"""
    codes_dict = read_codes_dict()

    # 收集所有非零值（已签到的学生ID）
    attended_students = [sid for code, sid in codes_dict.items() if sid != '0']

    # 将学生ID列表格式化为每个ID一行的文本
    return '\n'.join(attended_students)


if __name__ == '__main__':
    # 确保代码文件存在
    if not os.path.exists(CODES_FILE):
        generate_codes_file()

    # 启动应用程序
    app.run(host='localhost', port=80, debug=True)