#!/bin/bash

# conda activate qwen
# nohup bash qwen3_service.sh >run.log &

# 运行一个py文件，当它终止时重新启用，日志保存时间戳
PYTHON_SCRIPT="qwen3_service.py"

# 可选：指定 Python 解释器路径（如使用虚拟环境）
PYTHON_CMD="python"

mkdir -p log

# 无限循环，确保脚本崩溃后自动重启
while true; do
    
    LOG_FILE="log/qwen3_service_$(date +%Y%m%d_%H%M%S).log"
    # 运行 Python 脚本，并将python的所有输出追加到日志
    "$PYTHON_CMD" -u "$PYTHON_SCRIPT" >> "$LOG_FILE" 2>&1

    # 获取退出状态码
    EXIT_CODE=$?

    echo "[$(date)] Script exited with code $EXIT_CODE. Restarting in 10 seconds..." | tee -a "$LOG_FILE"
    
    # 等待几秒再重启，避免频繁崩溃导致系统负载过高
    sleep 10
done