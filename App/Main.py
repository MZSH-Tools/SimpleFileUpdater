"""
SimpleFileUpdater · Main
────────────────────────
启动入口：
1. 读取本地配置文件名（命令行可自定义）
2. 若文件首行是 URL → 在线加载键值对映射
   否则按本地键值对映射解析
3. 调用 FileSyncer.SyncFiles
"""

import sys, os, subprocess
from FileSyncer import SyncFiles, LoadConfigFromUrl

DEFAULT_CONFIG = ".SimpleFileUpdater"
CONFIG_FILE = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG


def LoadLocalOrRemoteConfig(file_name):
    """本地文件首行若是 URL → 远程解析；否则本地键值对"""
    with open(file_name, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        rest_text  = first_line + f.read()

    # 首行 URL
    if first_line.startswith("http"):
        mapping, err = LoadConfigFromUrl(first_line)
        return mapping, err

    # 本地键值对解析
    mapping = {}
    for line in rest_text.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = map(str.strip, line.split("=", 1))
            mapping[k] = v
    if mapping:
        return mapping, None
    return None, "本地配置为空或无法解析为键值对"


def Main():
    print("SimpleFileUpdater 启动中…")
    if not os.path.exists(CONFIG_FILE):
        print(f"未找到配置文件 {CONFIG_FILE}")
        input("\n按回车键退出…")
        return

    mapping, err = LoadLocalOrRemoteConfig(CONFIG_FILE)
    if err or not mapping:
        print("无法加载配置:", err)
        input("\n按回车键退出…")
        return

    SyncFiles(mapping)

    # 若映射中包含自身 → 完成后自动重启，当前进程直接结束
    if CONFIG_FILE in mapping:
        print("\n配置文件已更新，自动重启…")
        subprocess.Popen([sys.executable, __file__, CONFIG_FILE])
        return

    print("SimpleFileUpdater 完成")
    input("\n同步已结束，按回车键关闭窗口…")   # ←←← 等待用户

if __name__ == "__main__":
    Main()
