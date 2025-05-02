# SimpleFileUpdater

一个命令行文件更新工具，根据远程配置文件自动同步本地文件。

## 功能

- 从本地配置文件读取配置URL
- 从配置URL获取文件映射信息
- 使用MD5哈希值对比验证远程和本地文件
- 下载并更新需要更新的文件
- 在命令行中显示下载进度条
- 详细报告每个文件的处理状态

## 项目结构

- App/
  - Main.py: 主程序入口，读取配置并启动同步
  - FileSyncer.py: 包含同步逻辑、配置加载和MD5计算功能

## 使用方法

1. 确保已安装Python 3.6+和requests库
2. 在项目目录中创建`.SimpleFileUpdater`文件，内容为配置文件的URL
3. 运行程序: `python Main.py`
4. 如果配置文件不存在，程序会创建一个示例配置文件

## 配置文件格式

配置URL应指向一个JSON文件或其他可解析格式，内容为文件映射字典：

```json
{
    "path/to/local/file1.txt": "https://example.com/remote/file1.txt",
    "path/to/local/file2.jpg": "https://example.com/remote/file2.jpg"
}
