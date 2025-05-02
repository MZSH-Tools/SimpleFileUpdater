"""
SimpleFileUpdater · Main
────────────────────────
调用方式:
    SimpleFileUpdater.exe [ConfigFile]
说明:
1. 若参数缺省 → 默认 ".SimpleFileUpdater"
2. 配置文件首行若是 URL → 在线加载键值对映射
   否则将整个文件作为键值对映射解析
3. 同步完停在命令行等待用户回车，方便查看结果
"""

import sys, os
from FileSyncer import SyncFiles, LoadConfigFromUrl

DEFAULT_CONFIG = ".SimpleFileUpdater"
CONFIG_FILE    = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(DEFAULT_CONFIG)


def LoadLocalOrRemoteConfig(file_name: str):
    with open(file_name, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    if not lines:
        return None, "配置文件为空"

    first_line = lines[0].strip()

    # 首行 URL → 远程解析
    if first_line.startswith("http"):
        return LoadConfigFromUrl(first_line)

    # 本地键值对解析
    mapping = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = map(str.strip, line.split("=", 1))
            mapping[k] = v
    if mapping:
        return mapping, None
    return None, "无法解析为键值对格式"


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
    print("SimpleFileUpdater 完成")
    input("\n同步已结束，按回车键关闭窗口…")


if __name__ == "__main__":
    Main()
