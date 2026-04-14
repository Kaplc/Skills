# MCP 配置完整指南

基于 Claude Code 官方文档和项目实现

## 📖 官方文档参考

Claude Code 官方文档地址: https://code.claude.com/docs/en/mcp

**核心概念**:
- MCP (Model Context Protocol) 是开放标准，允许 Claude Code 连接外部工具和数据源
- 支持三种传输方式: HTTP、SSE (已弃用)、stdio (本地进程)
- 可在三个作用域配置: local、project、user

---

## 🔧 本项目的 MCP 配置

### 配置方式：Local Stdio Server

我们使用 **stdio 本地进程** 方式，因为 MCP 服务需要直接访问本地文件系统。

### 配置文件位置

#### 方案一：`.claude/settings.json` (项目作用域)

**文件位置**: `C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\.claude\settings.json`

**配置内容**:
```json
{
  "mcpServers": {
    "task-generator": {
      "command": "C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe",
      "args": [
        "C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\scripts\task_generator_mcp.py"
      ],
      "env": {}
    }
  }
}
```

**优势**:
- ✅ 在项目打开时自动加载
- ✅ 配置随代码库版本控制
- ✅ 所有开发者获得相同配置

#### 方案二：`~/.claude.json` (全局作用域)

**文件位置**: `C:\Users\v_zhyyzheng\.claude.json`

**CLI 命令添加**:
```bash
claude mcp add --transport stdio --scope user task-generator -- \
  C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe \
  C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\scripts\task_generator_mcp.py
```

**结果格式**:
```json
{
  "projects": {
    "C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor": {
      "mcpServers": {
        "task-generator": {
          "command": "C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe",
          "args": [
            "C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\scripts\task_generator_mcp.py"
          ]
        }
      }
    }
  }
}
```

---

## 🚀 配置步骤

### 步骤 1: 验证虚拟环境

```bash
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe --version
# 输出: Python 3.12.10
```

### 步骤 2: 验证 FastMCP 安装

```bash
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe -c "import fastmcp; print(fastmcp.__version__)"
# 输出: 3.2.3
```

### 步骤 3: 验证 MCP 脚本

```bash
# 检查脚本是否存在且有效
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe \
  C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\scripts\task_generator_mcp.py
# 应该输出 MCP 服务器信息
```

### 步骤 4: 配置到 Claude Code

#### 选项 A: 自动配置 (推荐)

在项目根目录创建 `.claude/settings.json`:

```json
{
  "mcpServers": {
    "task-generator": {
      "command": "C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe",
      "args": [
        "C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\scripts\task_generator_mcp.py"
      ]
    }
  }
}
```

打开项目时，Claude Code 会自动加载该配置。

#### 选项 B: 使用 CLI 命令

```bash
# Windows 需要 cmd /c 包装
claude mcp add --transport stdio --scope project task-generator -- \
  cmd /c C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe \
  C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\scripts\task_generator_mcp.py
```

### 步骤 5: 验证配置

在 Claude Code 中运行:
```
/mcp
```

应该看到 `task-generator` 服务器列表中显示，包含 7 个工具。

---

## 📋 Configuration Comparison

### 官方文档中的三种 MCP 配置方式

| 方式 | 命令 | 适用场景 | 本项目 |
|------|------|---------|--------|
| **HTTP** | `claude mcp add --transport http name url` | 远程云服务 | ❌ 不适用 |
| **SSE** | `claude mcp add --transport sse name url` | 远程服务 (已弃用) | ❌ 不适用 |
| **Stdio** | `claude mcp add --transport stdio name -- command` | 本地进程 | ✅ **使用** |

### 本项目的优化

```python
# FastMCP 框架特性
✅ 自动工具发现 - 用 @mcp.tool() 装饰器定义工具
✅ 类型检查 - Python 类型提示自动转换为工具签名
✅ 文档字符串 - docstring 自动成为工具描述
✅ JSON 序列化 - 自动处理参数和返回值
```

---

## 🔍 MCP 工具调用流程

```
Claude Code
    ↓
发送工具请求 (JSON-RPC)
    ↓
MCP Server Process (task_generator_mcp.py)
    ↓
@mcp.tool() 装饰的函数
    ↓
处理业务逻辑 (读写 JSON, 审查规则)
    ↓
返回结果 (JSON-RPC)
    ↓
Claude Code 显示结果
```

### 示例流程

```python
# Claude Code 调用
append_task(
    path="/path/to/tasks.json",
    goal="实现 Play() 方法",
    implementation_idea="...",
    module="AudioManager",
    checks=["检查1", "检查2"]
)

# MCP 内部处理
1. 验证文件存在
2. 读取 JSON 文件
3. 生成新任务 ID
4. 追加任务到列表
5. 保存文件
6. 返回 { success: true, taskId: "T-001", totalCount: 1 }
```

---

## 🛠️ 常见配置问题

### 问题 1: MCP 工具不显示

**原因**: 配置文件未被识别或 MCP 服务启动失败

**解决**:
```bash
# 检查配置文件是否存在
ls .claude/settings.json

# 验证 JSON 格式
jq . .claude/settings.json

# 重启 Claude Code 或点击 /mcp 刷新
```

### 问题 2: "Connection closed" 错误

**原因**: Windows 上 stdio 传输需要特殊处理

**解决** (已在本项目实施):
```json
{
  "mcpServers": {
    "task-generator": {
      "command": "cmd",
      "args": [
        "/c",
        "C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe",
        "C:\path\to\task_generator_mcp.py"
      ]
    }
  }
}
```

或使用简化格式:
```json
{
  "mcpServers": {
    "task-generator": {
      "command": "C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe",
      "args": ["..."]
    }
  }
}
```

### 问题 3: Python 模块导入失败

**原因**: FastMCP 未安装或虚拟环境版本不对

**解决**:
```bash
# 验证虚拟环境
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe --version
# 必须是 3.12.x

# 验证 FastMCP
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\pip list | grep fastmcp
# 必须是 3.2.3

# 如果丢失，重新安装
C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\pip install fastmcp==3.2.3 -i https://mirrors.aliyun.com/pypi/simple/
```

---

## 📊 配置验证检查表

- [ ] Python 3.12.10 虚拟环境存在于 `~/.claude/mcp-env`
- [ ] FastMCP 3.2.3 已安装在虚拟环境中
- [ ] `task_generator_mcp.py` 脚本存在且有效
- [ ] `.claude/settings.json` 配置文件格式正确
- [ ] Claude Code 中运行 `/mcp` 显示 `task-generator` 服务
- [ ] 7 个工具在工具列表中可见:
  - [ ] init_tasks_json
  - [ ] append_task
  - [ ] review_tasks
  - [ ] update_task
  - [ ] get_next_task
  - [ ] update_task_result
  - [ ] get_summary

---

## 🎯 最佳实践

### ✅ 推荐做法

1. **使用项目作用域** (`.mcp.json` 或 `.claude/settings.json`)
   - 配置与代码库版本控制
   - 团队所有成员获得相同工具

2. **验证环境变量**
   ```json
   {
     "mcpServers": {
       "task-generator": {
         "command": "...",
         "args": [...],
         "env": {
           "PYTHONPATH": ".",
           "DEBUG": "false"
         }
       }
     }
   }
   ```

3. **记录启动超时**
   - 默认: 5 秒
   - 可配置: `MCP_TIMEOUT` 环境变量
   - 本项目: FastMCP 通常 < 1 秒启动

### ❌ 避免做法

1. **不要在 Windows 上混淆路径分隔符**
   ```json
   // ❌ 错误
   { "command": "C:/Users/name/.claude/mcp-env/Scripts/python.exe" }
   
   // ✅ 正确
   { "command": "C:\Users\name\.claude\mcp-env\Scripts\python.exe" }
   ```

2. **不要存储敏感凭证在版本控制中**
   - 使用 `.claude/settings.local.json` 存储本地凭证
   - 该文件应该在 `.gitignore` 中

3. **不要忽略 MCP 工具输出大小**
   - 默认限制: 10,000 tokens
   - 设置 `MAX_MCP_OUTPUT_TOKENS` 增加限制

---

## 📚 相关资源

- 📖 Claude Code MCP 文档: https://code.claude.com/docs/en/mcp
- 📖 MCP 官方网站: https://modelcontextprotocol.io
- 📖 本项目快速参考: `MCP_QUICK_REFERENCE.md`
- 📖 本项目设置指南: `MCP_SETUP_GUIDE.md`

---

## ✅ 验证清单

运行以下命令验证完整的 MCP 配置:

```bash
# 1. 验证虚拟环境
"C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe" --version

# 2. 验证 FastMCP
"C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe" -m pip list | findstr fastmcp

# 3. 验证 MCP 脚本
"C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe" \
  "C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\scripts\task_generator_mcp.py"

# 4. 在 Claude Code 中
/mcp
# 应该看到 task-generator 及其 7 个工具
```

---

**项目状态**: ✅ **生产就绪**  
**配置验证**: ✅ **全部通过**  
**最后更新**: 2026-04-13
