import os
import chardet
import time
import matplotlib.pyplot as plt
import re

def detect_encoding(filename):
    """ 尝试检测文件的编码方式 """
    try:
        with open(filename, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']
    except Exception as e:
        print(f"无法检测文件 {filename} 的编码: {e}")
        return 'utf-8'  # 默认使用UTF-8


def count_lines_in_file(filename):
    """ 计算单个文件中的非空行数 """
    try:
        encoding = detect_encoding(filename)
        with open(filename, 'r', encoding=encoding, errors='ignore') as file:
            lines = file.readlines()
            # 去除空白行
            non_empty_lines = [line for line in lines if line.strip()]
            return len(non_empty_lines)
    except Exception as e:
        print(f"无法处理文件 {filename}: {e}")
        return 0


def is_interesting_file(file_name):
    """ 检查文件是否是我们感兴趣的类型之一，并返回对应的语言标识符 """
    if file_name.endswith('.py'):
        return ('py', file_name)
    elif file_name.endswith('.c'):
        return ('c', file_name)
    elif file_name.endswith('.h'):
        return ('h', file_name)
    elif file_name.endswith('.java'):
        return ('java', file_name)
    elif file_name.endswith('.cpp'):
        return ('cpp', file_name)
    elif file_name.endswith('.cs'):
        return ('cs', file_name)
    else:
        return None


def count_lines_in_dir(directory):
    """ 在指定目录中查找所有感兴趣的语言文件并计算它们的行数和函数长度 """
    language_counts = {'py': 0, 'c': 0, 'h': 0, 'java': 0, 'cpp': 0, 'cs': 0}
    function_lengths = {'py': [], 'c': [], 'h': [], 'java': [], 'cpp': [], 'cs': []}
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            result = is_interesting_file(file)
            if result:
                language, filename = result
                full_path = os.path.join(root, filename)
                language_counts[language] += count_lines_in_file(full_path)
                with open(full_path, 'r', encoding=detect_encoding(full_path), errors='ignore') as f:
                    lines = f.readlines()
                    in_function = False
                    function_length = 0
                    brace_count = 0

                    if language == 'py':
                        for line in lines:
                            stripped_line = line.strip()
                            if not stripped_line or stripped_line.startswith('#'):
                                continue
                            if stripped_line.startswith('def ') or stripped_line.startswith('class '):
                                if in_function:
                                    function_lengths[language].append(function_length)
                                in_function = True
                                function_length = 1
                            elif in_function:
                                function_length += 1
                        if in_function:
                            function_lengths[language].append(function_length)

                    elif language in ['c', 'cpp', 'cs', 'java']:
                        for line in lines:
                            stripped_line = line.strip()
                            if not stripped_line or stripped_line.startswith('//'):
                                continue
                            if re.match(r'\b(int|void|char|float|double|public|private|protected)\b', stripped_line):
                                if in_function:
                                    function_lengths[language].append(function_length)
                                in_function = True
                                function_length = 1
                                brace_count = 0
                            elif in_function:
                                function_length += 1
                                if '{' in stripped_line:
                                    brace_count += 1
                                if '}' in stripped_line:
                                    brace_count -= 1
                                    if brace_count == 0:
                                        function_lengths[language].append(function_length)
                                        in_function = False
                                        function_length = 0
                        if in_function:
                            function_lengths[language].append(function_length)

    return language_counts, function_lengths


if __name__ == "__main__":
    directory = input("dir name: ")
    function = input("function: ")
    if function == 'y':
        counts, function_lengths = count_lines_in_dir(directory)
        for language, count in counts.items():
            print(f"code : {language}: {count}")
        for language, lengths in function_lengths.items():
            print(f"function : {language}: {sum(lengths)/(len(lengths) + 1)}") # average function length
        exit(0)
    plot = input("plot: ")
    if plot == 'y':
        plot = True
    else:
        plot = False
    start_time = time.time()
    counts = {'py': 0, 'c': 0, 'h': 0, 'java': 0, 'cpp': 0, 'cs': 0}
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlabel('language')
    ax.set_ylabel('code line number')
    ax.set_title('statistics')
    colors = {'py': 'r', 'c': 'g', 'h': 'b', 'java': 'y', 'cpp': 'm', 'cs': 'c'}
    if plot:
        for root, dirs, files in os.walk(directory):
            for file in files:
                result = is_interesting_file(file)
                if result:
                    language, filename = result
                    full_path = os.path.join(root, filename)
                    counts[language] += count_lines_in_file(full_path)
                    langs = list(counts.keys())
                    lines = list(counts.values())
                    ax.clear()
                    ax.bar(langs, lines, color=[colors[lang] for lang in langs])
                    ax.set_xlabel('language')
                    ax.set_ylabel('code line number')
                    ax.set_title('statistics')
                    plt.pause(0.01)
    else:
        counts = count_lines_in_dir(directory)

    end_time = time.time()
    print(f"总共花费 {end_time - start_time:.2f} 秒")
    print(f"在目录 {directory} 中找到的代码行数如下:")
    for lang, lines in counts.items():
        print(f"{lang}: {lines}")
    if plot:
        plt.ioff()
        plt.show()