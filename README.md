# SimpleFileUpdater 使用指南（本地键值对版本）

SimpleFileUpdater 是一个轻量级的文件同步工具，适用于希望从远程地址批量更新本地文件的用户。程序已打包为 `SimpleFileUpdater.exe`，支持通过配置文件定义目标文件及其下载地址。

---

## 🧩 配置文件说明

默认配置文件为 **`.SimpleFileUpdater`**，内容格式如下：

```
# 每行一个映射：本地路径 = 远程 URL
Tools\MyTool.exe = https://example.com/releases/MyTool.exe
Docs\Manual.pdf  = https://cdn.example.com/docs/Manual.pdf
```

- 支持相对路径或绝对路径
- 自动创建所需文件夹
- 支持注释（以 `#` 开头）

---

## 🚀 如何运行

将 `SimpleFileUpdater.exe` 与 `.SimpleFileUpdater` 放在同一目录，然后：

- **双击 `SimpleFileUpdater.exe`**，程序将自动读取配置文件并同步所需文件
- 或者通过命令行运行：

```bash
SimpleFileUpdater.exe MyConfig.txt
```

执行完成后程序会停留在命令行，等待用户按回车查看结果。

---

## 🧪 如何从源码运行（开发者或未打包场景）

本项目提供了两种方式用于一键搭建运行环境：

### 方式 1：使用 Conda（推荐）

```bash
conda env create -f environment.yml
conda activate SimpleFileUpdater
python App/Main.py
```

### 方式 2：使用 pip

```bash
pip install -r requirements.txt
python App/Main.py
```

---

## 📄 许可证 License

本项目已包含如下许可证：

```
（以下内容自动读取 LICENSE 文件中内容，请查看项目根目录中的 LICENSE 文件）
```

---

## ⚠️ 免责声明

本项目为个人工具项目，使用者需自行承担使用本工具所带来的风险。  
请自行确认远程文件地址的可靠性与安全性，程序可能会覆盖本地同名文件，请提前备份。

---

本地文件同步，从未如此简单。Enjoy!