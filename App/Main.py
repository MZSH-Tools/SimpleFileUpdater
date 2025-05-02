import os
# 修改导入方式，使其在不同目录结构下都能正确工作
try:
    from FileSyncer import SyncFiles, LoadConfigFromUrl
except ImportError:
    from App.FileSyncer import SyncFiles, LoadConfigFromUrl

def CreateConfigFileTemplate():
    """创建示例配置文件"""
    ConfigFile = ".SimpleFileUpdater"
    with open(ConfigFile, "w") as File:
        File.write("https://example.com/.filemap")
    
    print(f"已创建示例配置文件 '{ConfigFile}'")
    print("请编辑此文件并添加您的配置URL，然后重新运行程序")
    print("配置URL应指向一个包含文件映射的简单键值对文件")
    print("配置文件格式示例 (每行一个键值对):")
    print('''
# 这是一个简单的键值对配置文件
# 格式: 本地文件路径 = 远程URL

path/to/local/file1.txt = https://example.com/remote/file1.txt
path/to/local/file2.jpg = https://example.com/remote/file2.jpg
docs/README.md = https://raw.githubusercontent.com/example/project/main/README.md
''')

def Main():
    """
    SimpleFileUpdater 主入口函数
    """
    print("SimpleFileUpdater 启动中...")
    
    # 检查配置文件是否存在
    ConfigFile = ".SimpleFileUpdater"
    if not os.path.exists(ConfigFile):
        print(f"错误: 未找到配置文件 '{ConfigFile}'")
        CreateConfigFileTemplate()
        return
    
    # 读取配置URL
    try:
        with open(ConfigFile, "r") as File:
            ConfigUrl = File.readline().strip()
        
        if not ConfigUrl:
            print(f"错误: 配置文件 '{ConfigFile}' 为空")
            print("请在配置文件中添加您的配置URL")
            return
    except Exception as Error:
        print(f"读取配置文件时出错: {str(Error)}")
        return
    
    # 从URL加载文件映射配置
    FileMapping, Error = LoadConfigFromUrl(ConfigUrl)
    
    if Error or not FileMapping:
        print(f"无法加载配置: {Error}")
        return
    
    if not isinstance(FileMapping, dict) or not FileMapping:
        print("错误: 配置格式不正确或为空")
        print("配置应为包含文件映射的字典/JSON对象")
        return
    
    # 调用同步函数
    SyncFiles(FileMapping)
    
    print("SimpleFileUpdater 完成")

if __name__ == "__main__":
    try:
        Main()
    except KeyboardInterrupt:
        print("\n程序已被用户中断")
    except Exception as Error:
        print(f"程序运行时出现错误: {str(Error)}")