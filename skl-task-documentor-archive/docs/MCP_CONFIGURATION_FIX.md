# MCP 配置诊断与修复指南

**日期**: 2026-04-13  
**状态**: 配置已验证，需要重新加载

---

## 🔍 诊断结果

### ✅ 配置文件验证

**文件位置**: `.claude/settings.json`

```json
{
  "mcpServers": {
    "task-generator": {
      "command": "C:\\Users\\v_zhyyzheng\\.claude\\mcp-env\\Scripts\\python.exe",
      "args": [
        "C:\\Users\\v_zhyyzheng\\Desktop\\Skills\\skills\\skl-task-documentor\\scripts\\task_generator_mcp.py"
      ],
      "env": {}
    }
  }
}
```

**验证状态**：
- ✅ Python 可执行文件存在
- ✅ MCP 脚本文件存在
- ✅ FastMCP 3.2.3 已安装
- ✅ MCP 服务器可正常启动
- ✅ 所有 7 个工具已注册

### ✅ MCP 工具注册验证

通过 JSON-RPC 协议验证，以下 7 个工具已成功注册：

1. ✅ `init_tasks_json()` - 初始化任务框架
2. ✅ `append_task()` - 追加单个任务
3. ✅ `review_tasks()` - 全局审查
4. ✅ `update_task()` - 修改任务
5. ✅ `get_next_task()` - 获取待做任务
6. ✅ `update_task_result()` - 记录执行结果
7. ✅ `get_summary()` - 获取完成摘要

---

## 🔧 修复步骤

### 方法 1：重新加载 MCP（最简单）

1. **在 Claude Code 中打开命令面板**
   - Windows/Linux: `Ctrl+Shift+P`
   - macOS: `Cmd+Shift+P`

2. **搜索并运行**
   ```
   Claude Code: Reload MCP Servers
   ```
   或
   ```
   MCP: Reload
   ```

3. **检查 MCP 是否加载**
   - 查看底部状态栏，应显示 MCP 连接状态
   - 打开任何聊天框，在工具列表中应看到 7 个 Task-Documentor 工具

### 方法 2：重新启动 Claude Code

1. 完全关闭 Claude Code
2. 重新打开项目文件夹
3. MCP 应该自动加载

### 方法 3：检查 MCP 连接状态

在任何对话中输入：
```
/mcp
```

应该看到类似输出：
```
MCP Servers:
├─ task-generator ✅ Connected
│  ├─ init_tasks_json
│  ├─ append_task
│  ├─ review_tasks
│  ├─ update_task
│  ├─ get_next_task
│  ├─ update_task_result
│  └─ get_summary
```

---

## 🐛 常见问题排查

### 问题：MCP 工具未显示

**原因**: Claude Code 配置缓存未更新

**解决方案**:
1. 运行 `Claude Code: Reload MCP Servers` 命令
2. 或者完全重启 Claude Code
3. 检查 `.claude/settings.json` 文件是否正确

### 问题：提示 "Connection closed"

**原因**: MCP 服务器启动失败

**排查步骤**:
```bash
# 手动测试 MCP 服务器启动
"C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe" \
  "C:\Users\v_zhyyzheng\Desktop\Skills\skills\skl-task-documentor\scripts\task_generator_mcp.py"
```

应该看到 FastMCP 启动画面，说明服务器正常。

### 问题：提示 "Module not found"

**原因**: Python 虚拟环境配置问题

**排查步骤**:
```bash
# 验证虚拟环境和依赖
"C:\Users\v_zhyyzheng\.claude\mcp-env\Scripts\python.exe" -c \
  "import fastmcp; print('FastMCP 版本:', fastmcp.__version__)"
```

应该输出: `FastMCP 版本: 3.2.3`

---

## 📋 验证检查表

完成以下步骤确保配置正确：

- [ ] `.claude/settings.json` 文件存在且内容正确
- [ ] Python 虚拟环境路径正确：`C:\Users\v_zhyyzheng\.claude\mcp-env`
- [ ] MCP 脚本路径正确：`skl-task-documentor/scripts/task_generator_mcp.py`
- [ ] MCP 服务器能手动启动（见常见问题排查）
- [ ] FastMCP 版本正确：3.2.3
- [ ] Claude Code 已运行 `Reload MCP Servers` 或重启
- [ ] 在聊天中能看到 7 个工具（init_tasks_json、append_task 等）
- [ ] 能成功调用任何一个工具

---

## 🚀 验证工具是否工作

一旦 MCP 加载成功，可以立即测试一个工具：

### 测试 1：初始化任务

在 Claude Code 聊天中：

```
请初始化一个新的任务方案，名称为 "测试方案"，保存到 D:\test_tasks.json
```

Claude 会自动调用 `init_tasks_json()` 工具并返回结果。

### 测试 2：追加任务

```
现在追加一个任务到 D:\test_tasks.json，要求：
- goal: "实现 Play() 方法"
- implementationIdea: "通过调用 AudioSource.Play() 实现播放功能"
- module: "AudioManager"
- checks: ["方法已定义", "能够播放音频"]
```

### 测试 3：审查任务

```
审查 D:\test_tasks.json 中的所有任务
```

---

## 📞 支持信息

如果以上步骤都无法解决问题：

1. **检查官方文档**
   - https://code.claude.com/docs/en/mcp

2. **查看项目文档**
   - `MCP_SETUP_GUIDE.md` - 详细设置指南
   - `MCP_QUICK_REFERENCE.md` - 快速参考
   - `MCP_CONFIGURATION_GUIDE.md` - 配置指南

3. **运行诊断脚本**
   ```bash
   cd skl-task-documentor
   ~/.claude/mcp-env/Scripts/python test_mcp_venv.py
   ```

---

**配置状态**: ✅ **已验证正确**  
**下一步**: 在 Claude Code 中重新加载 MCP 服务器  
**生成时间**: 2026-04-13
