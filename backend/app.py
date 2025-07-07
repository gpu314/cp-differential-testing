import os
import random
import subprocess
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

NUM_TESTS = 100

# def generate_test_case():
#     quarters = random.randint(1, 99)
#     m1 = random.randint(0, 34)
#     m2 = random.randint(0, 99)
#     m3 = random.randint(0, 9)
#     return f"{quarters}\n{m1}\n{m2}\n{m3}\n"

def generate_test_case():
    return f"{random.randint(1, 99)}\n"

def run_python(code, input_str):
    with tempfile.NamedTemporaryFile("w+", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        path = f.name

    try:
        result = subprocess.run(["python3", path], input=input_str, text=True, capture_output=True, timeout=5)
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return "", "Python code timed out"
    finally:
        os.remove(path)

import re

def java_class_name(code):
    match = re.search(r'public\s+class\s+([A-Za-z_][A-Za-z0-9_]*)', code)
    return match.group(1) if match else None

def run_java(code, input_str):
    class_name = java_class_name(code)
    if not class_name:
        return "", "Could not find public class declaration in Java code"

    with tempfile.TemporaryDirectory() as temp_dir:
        java_file_path = os.path.join(temp_dir, f"{class_name}.java")

        with open(java_file_path, "w") as f:
            f.write(code)

        compile_result = subprocess.run(
            ["javac", java_file_path],
            capture_output=True,
            text=True
        )

        if compile_result.returncode != 0:
            return "", f"Java compile error:\n{compile_result.stderr}"

        try:
            result = subprocess.run(
                ["java", "-cp", temp_dir, class_name],
                input=input_str,
                text=True,
                capture_output=True,
                timeout=5
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return "", "Java code timed out"

def run_cpp(code, input_str):
    with tempfile.TemporaryDirectory() as temp_dir:
        cpp_file = os.path.join(temp_dir, "solution.cpp")
        binary_file = os.path.join(temp_dir, "solution.out")

        with open(cpp_file, "w") as f:
            f.write(code)

        compile_result = subprocess.run(
            ["g++", cpp_file, "-o", binary_file],
            capture_output=True,
            text=True
        )
        if compile_result.returncode != 0:
            return "", f"C++ compile error:\n{compile_result.stderr}"

        try:
            result = subprocess.run(
                [binary_file],
                input=input_str,
                text=True,
                capture_output=True,
                timeout=5
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return "", "C++ code timed out"

@app.route("/api/run", methods=["POST"])
def run_differential_test():
    data = request.json
    slow_lang = data.get("slowLang")
    fast_lang = data.get("fastLang")
    slow_code = data.get("slowCode")
    fast_code = data.get("fastCode")

    if not (slow_code and fast_code):
        return jsonify({"error": "Both code inputs are required"}), 400

    for i in range(1, NUM_TESTS + 1):
        test_input = generate_test_case()

        # Run slow code
        if slow_lang == "python":
            slow_out, slow_err = run_python(slow_code, test_input)
        elif slow_lang == "java":
            slow_out, slow_err = run_java(slow_code, test_input)
        elif slow_lang == "cpp":
            slow_out, slow_err = run_cpp(slow_code, test_input)
        else:
            return jsonify({"error": f"Unsupported slow language: {slow_lang}"}), 400

        # Run fast code
        if fast_lang == "python":
            fast_out, fast_err = run_python(fast_code, test_input)
        elif fast_lang == "java":
            fast_out, fast_err = run_java(fast_code, test_input)
        elif fast_lang == "cpp":
            fast_out, fast_err = run_cpp(fast_code, test_input)
        else:
            return jsonify({"error": f"Unsupported fast language: {fast_lang}"}), 400

        if slow_err or fast_err:
            return jsonify({
                "match": False,
                "test_number": i,
                "test_input": test_input,
                "slow_output": slow_out,
                "fast_output": fast_out,
                "slow_error": slow_err,
                "fast_error": fast_err
            })

        if slow_out != fast_out:
            return jsonify({
                "match": False,
                "test_number": i,
                "test_input": test_input,
                "slow_output": slow_out,
                "fast_output": fast_out,
                "slow_error": slow_err,
                "fast_error": fast_err
            })

    return jsonify({"match": True, "message": f"All {NUM_TESTS} test cases matched!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))