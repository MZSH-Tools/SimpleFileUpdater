import sys, os
from FileSyncer import SyncFiles

DEFAULT_CONFIG = ".SimpleFileUpdater"
CONFIG_FILE    = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.abspath(DEFAULT_CONFIG)

def LoadLocalMapping(file_name: str):
    if not os.path.exists(file_name):
        return None, f"配置文件 '{file_name}' 不存在"

    with open(file_name, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    mapping = {}
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = map(str.strip, line.split("=", 1))
            mapping[k] = v

    if mapping:
        return mapping, None
    return None, "配置为空或无有效键值对"

def main():
    print("SimpleFileUpdater 启动中…")

    mapping, err = LoadLocalMapping(CONFIG_FILE)
    if err:
        print("加载配置失败:", err)
        input("\n按回车键退出…")
        return

    SyncFiles(mapping)
    print("SimpleFileUpdater 完成")
    input("\n同步已结束，按回车键关闭窗口…")

if __name__ == "__main__":
    main()