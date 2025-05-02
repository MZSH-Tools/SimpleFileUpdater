# SimpleFileUpdater

一个轻量、通用的文件同步工具。你只需要提供一个远程文件映射配置，它就会自动从远程地址下载、校验并更新本地文件。

---

## ✨ 功能特性

- 支持任意 HTTP 地址的文件同步
- 支持 JSON 或键值对格式的远程配置文件
- 自动计算 MD5 检查文件是否需要更新
- 同步前自动创建缺失的本地目录
- 详细的命令行进度与状态反馈
- 网络异常自动跳过，不影响整体流程

---

## 📁 项目结构

```
SimpleFileUpdater/
├── App/
│   ├── FileSyncer.py   # 文件同步核心逻辑
│   └── Main.py         # 程序入口，读取配置并执行同步
├── .SimpleFileUpdater  # 用户配置文件（需手动创建，指向配置URL）
├── environment.yml     # Conda 环境导出（可选）
├── requirements.txt    # pip 依赖列表（可选）
└── LICENSE             # 项目许可证
```

---

## 🚀 使用说明

### 1. 准备 Python 环境

推荐使用 Conda 或 Python 3.11+ 环境：

```bash
conda create -n SimpleFileUpdater python=3.11
conda activate SimpleFileUpdater
pip install -r requirements.txt
```

或使用已有环境手动安装：
```bash
pip install requests
```

---

### 2. 创建配置文件 `.SimpleFileUpdater`

该文件中应包含远程配置地址，如：

```
https://example.com/file-map.txt
```

---

### 3. 远程配置格式说明

配置文件支持两种格式：

#### ✅ 格式一：键值对（推荐）

```
path/to/local/file1.exe = https://yourcdn.com/bin/file1.exe
path/to/local/Config.json = https://example.com/config.json
```

#### ✅ 格式二：JSON 字典

```json
{
  "bin/Tool.exe": "https://example.com/releases/Tool.exe",
  "assets/logo.png": "https://cdn.com/logo.png"
}
```

---

### 4. 执行同步命令

```bash
python App/Main.py
```

程序将自动读取配置，下载远程文件并覆盖本地旧版本。

---

## 🛡️ 错误处理与健壮性

- 如果下载失败，程序将记录错误并跳过该文件
- 本地文件若不存在，将自动创建路径并写入
- 支持显示进度条

---

## 📝 License

本项目遵循 [MIT License](./LICENSE)。

---

## 🤝 贡献建议

欢迎提交 Issue 或 PR 来改进本项目。建议遵循 PascalCase 命名风格。