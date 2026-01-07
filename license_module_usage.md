# Python -m 命令使用指南

## 命令格式说明

### 基本格式
```powershell
# 完整格式
C:/Users/Administrator/python-sdk/python3.13.2/python.exe -m [包名].[模块名]

# 简化格式（当Python已添加到环境变量时）
python -m [包名].[模块名]
```

### 参数说明
- `C:/Users/Administrator/python-sdk/python3.13.2/python.exe`：Python解释器的完整路径
- `-m`：模块运行标志，告诉Python将指定的模块作为脚本执行
- `[包名].[模块名]`：要运行的模块的完整名称（包名+模块名）

## 注册系统模块运行示例

### 1. 测试硬件信息获取
```powershell
# 完整命令
C:/Users/Administrator/python-sdk/python3.13.2/python.exe -m license.hardware_info

# 简化命令（Python已添加到环境变量时）
python -m license.hardware_info
```

**功能**：获取当前设备的硬件信息，包括主板序列号、MAC地址、CPU信息、磁盘序列号和唯一机器ID。

### 2. 测试注册码生成器
```powershell
# 完整命令
C:/Users/Administrator/python-sdk/python3.13.2/python.exe -m license.license_generator

# 简化命令
python -m license.license_generator
```

**功能**：生成RSA密钥对，并为测试机器生成试用版、标准版和企业版注册码，然后验证这些注册码。

### 3. 测试注册管理器
```powershell
# 完整命令
C:/Users/Administrator/python-sdk/python3.13.2/python.exe -m license.license_manager

# 简化命令
python -m license.license_manager
```

**功能**：初始化注册管理器，获取注册状态和机器ID。

### 4. 测试注册信息存储
```powershell
# 完整命令
C:/Users/Administrator/python-sdk/python3.13.2/python.exe -m license.license_store

# 简化命令
python -m license.license_store
```

**功能**：测试注册信息的加密存储和加载功能。

## 使用注意事项

1. **必须在项目根目录下运行**：执行命令时，当前工作目录必须是项目的根目录（即包含 `main.py` 和 `license` 文件夹的目录）。

2. **完整的Python路径**：如果Python没有添加到系统环境变量，必须使用完整的Python解释器路径。

3. **包和模块名称**：包名和模块名必须正确，区分大小写。

4. **避免相对导入错误**：使用 `-m` 方式运行可以确保模块在正确的包上下文中执行，避免直接运行包内模块导致的相对导入错误。

## 适用场景

### 开发测试时
- 测试单个模块的功能
- 调试模块之间的交互
- 验证模块的独立运行能力

### 学习和理解时
- 查看模块的输出结果
- 理解模块的工作原理
- 学习Python包的结构和使用

### 生产环境中
- 作为脚本运行特定功能
- 自动化测试和验证
- 批量生成注册码

## 对比直接运行

| 运行方式 | 命令格式 | 适用场景 | 优势 | 劣势 |
|---------|---------|---------|------|------|
| -m 方式 | `python -m license.xxx` | 开发测试、生产运行 | 避免相对导入错误、包上下文正确 | 需要在项目根目录运行 |
| 直接运行 | `python license/xxx.py` | 简单测试、快速验证 | 无需考虑包结构 | 可能出现相对导入错误 |

## 总结

使用 `python -m` 方式运行模块是一种更加规范和安全的做法，特别是对于复杂的Python包结构。它可以确保模块在正确的上下文中执行，避免相对导入错误，同时提供了更好的可维护性和可扩展性。

对于注册系统来说，推荐使用 `-m` 方式进行开发测试和生产运行，以确保系统的稳定性和可靠性。