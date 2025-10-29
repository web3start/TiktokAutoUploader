from tiktok_uploader import cookies
import os
import json

# -----------------------------------------------------------------
# 1. 定义要读取的 cookie 文件名
cookie_filename = "www.tiktok.com_cookies.json"

# 2. 从文件读取并加载 JSON
try:
    # 使用 'utf-8' 编码打开文件
    with open(cookie_filename, 'r', encoding='utf-8') as f:
        my_cookie_list_raw = json.load(f)
    print(f"成功从 {cookie_filename} 读取 cookie。")
except FileNotFoundError:
    print(f"错误：未找到 cookie 文件 '{cookie_filename}'。")
    print("请确保该文件与您的 Python 脚本在同一个目录下。")
    exit() # 找不到文件，直接退出
except json.JSONDecodeError:
    print(f"错误：无法解析 '{cookie_filename}'。")
    print("请确保文件内容是有效的 JSON 格式（通常以 '[' 开头，以 ']' 结尾）。")
    exit() # JSON 格式错误, 直接退出
except Exception as e:
    print(f"读取文件时发生未知错误: {e}")
    exit() # 其他错误, 直接退出
# -----------------------------------------------------------------

# 3. 准备处理列表 (基本同原脚本)
my_cookie_list_processed = []


# --- 修复代码：过滤掉导致冲突的 'msToken' ---
# (这部分逻辑来自您的原始脚本，予以保留)
filtered_list_raw = [
    cookie for cookie in my_cookie_list_raw
    if not (cookie.get('name') == 'msToken' and cookie.get('domain') == 'www.tiktok.com')
]
# --- 修复代码结束 ---


# 4. 遍历这个 *过滤后* 的列表 (原脚本的 "3. 遍历")
for cookie in filtered_list_raw:
    # 移除 'storeId' 和 'session' (如果存在)
    cookie.pop('storeId', None)
    cookie.pop('session', None)

    # 关键：重命名 'expirationDate' 为 'expiry'
    if 'expirationDate' in cookie:
        # 将浮点数时间戳转换为整数
        cookie['expiry'] = int(cookie.pop('expirationDate'))

    my_cookie_list_processed.append(cookie)


# 5. 使用正确的命名规则 (原脚本的 "4. 命名规则")
login_name = "ipanda"
filename_to_save = f"tiktok_session-{login_name}"


# 6. 调用函数保存文件 (原脚本的 "5. 调用函数")
cookies.save_cookies_to_file(my_cookie_list_processed, filename_to_save)

print(f"成功为用户 '{login_name}' 从文件创建了 *已修复* 的 cookie 文件。")
