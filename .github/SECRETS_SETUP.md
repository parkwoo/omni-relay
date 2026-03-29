# GitHub Secrets 设置指南

## API Keys（全部可选）

**好消息：所有 API Keys 都是完全可选的！**

系统使用 fallback 数据可以正常运行。API Keys 只是启用实时数据收集。

### 推荐设置（获取最新数据）

| 厂商 | 必需 | 用途 | 免费额度 |
|------|------|------|---------|
| **OpenRouter** | ⭐ 推荐 | 动态获取 30+ 免费模型 | 完全免费 |
| **Novita AI** | ⭐ 推荐 | 获取 Novita 模型列表 | $20 |
| **Kilo Gateway** | ⭐ 推荐 | 获取 Kilo 500+ 模型 | $5 |
| **Google Gemini** | ❌ 可选 | 验证 Gemini 模型 | 1M tokens/min |

---

## 对比

### ❌ 不设置 API Keys

**优点：**
- 无需注册任何账号
- 设置简单，零配置
- 完全免费

**缺点：**
- 使用 fallback 数据（基于官方文档）
- 新免费模型可能延迟发现
- 无法验证模型变化

**适用场景：**
- 个人项目
- 免费模型信息稳定
- 不想管理 API Keys

---

### ✅ 设置 API Keys

**优点：**
- 实时获取最新模型信息
- OpenRouter 新模型第一时间发现
- 自动验证模型可用性

**缺点：**
- 需要注册 3 个账号
- 需要管理 API Keys

**适用场景：**
- 追求最新数据
- 生产环境
- 自动化需求高

---

## 获取步骤（如果决定设置）

### 1. OpenRouter API Key ⭐ 最重要

**用途：** 动态获取 30+ 个免费 AI 模型  
**成本：** 完全免费，无需信用卡  
**获取时间：** 2 分钟

#### 获取步骤：
1. 访问 https://openrouter.ai/keys
2. 点击 "Sign In" 使用 GitHub 或 Google 账号登录
3. 登录后自动创建 API Key
4. 复制 Key（格式：`sk-or-v1-xxxxxxxx`）
5. 添加到 GitHub Secrets

```bash
# GitHub 操作：
Repository → Settings → Secrets and variables → Actions → New repository secret

Name:  OPENROUTER_API_KEY
Value: sk-or-v1-xxxxxxxxxxxxx
```

---

### 2. Novita AI API Key

**用途：** 获取 Novita 平台模型列表  
**成本：** 注册送 $20 免费额度  
**获取时间：** 3 分钟

#### 获取步骤：
1. 访问 https://novita.ai
2. 点击右上角 "Sign Up" 注册账号
3. 登录后进入 Dashboard
4. 左侧菜单 "API Keys" → 创建新 Key
5. 复制 Key

```bash
# GitHub Secrets:
Name:  NOVITA_API_KEY
Value: your-novita-api-key
```

---

### 3. Kilo Gateway API Key

**用途：** 获取 Kilo Gateway 500+ 模型列表  
**成本：** 注册送 $5 免费额度  
**获取时间：** 3 分钟

#### 获取步骤：
1. 访问 https://kilo.ai
2. 点击 "Sign Up" 注册账号
3. 进入 Settings → API Keys
4. 生成新 API Key
5. 复制 Key

```bash
# GitHub Secrets:
Name:  KILOCODE_API_KEY
Value: your-kilo-api-key
```

---

### 4. Google Gemini API Key (可选)

**用途：** 验证 Gemini 最新模型  
**成本：** 免费额度 1M tokens/分钟  
**获取时间：** 5 分钟

#### 获取步骤：
1. 访问 https://aistudio.google.com/app/apikey
2. 使用 Google 账号登录
3. 点击 "Create API Key"
4. 复制 Key

```bash
# GitHub Secrets (Optional):
Name:  GEMINI_API_KEY
Value: AIzaSyxxxxxxxxxxxxx
```

---

## 快速设置（推荐）

**最少配置（只设置 OpenRouter）：**
```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

**完整配置（推荐）：**
```bash
OPENROUTER_API_KEY=sk-or-v1-...
NOVITA_API_KEY=novita-...
KILOCODE_API_KEY=kilo-...
GEMINI_API_KEY=AIza...
```

---

## 验证设置

设置完成后，手动触发工作流验证：

1. 访问 GitHub Actions
2. 点击 "Update Model Database"
3. 点击 "Run workflow"
4. 等待运行完成
5. 检查生成的 Pull Request

---

## 常见问题

### Q: 不设置 API Key 会怎样？
A: 系统会使用 fallback 数据（基于官方文档的静态数据），可能不是最新的。

### Q: API Key 安全吗？
A: 非常安全。GitHub Secrets 是加密存储的，只有你的工作流能访问。

### Q: 免费额度够用吗？
A: 完全够用！模型收集脚本每 3 天运行一次，每次只调用几次 API，远低于免费额度。

### Q: 可以只设置部分 Key 吗？
A: 可以！建议至少设置 `OPENROUTER_API_KEY`，其他可选。

---

## 费用估算

| 厂商 | 免费额度 | 脚本消耗 | 是否收费 |
|------|---------|---------|---------|
| OpenRouter | 免费模型 | ~10 次请求/3 天 | ❌ 免费 |
| Novita | $20 | ~1 次请求/3 天 | ❌ 免费 |
| Kilo | $5 | ~1 次请求/3 天 | ❌ 免费 |
| Gemini | 1M tokens/min | ~1 次请求/3 天 | ❌ 免费 |

**总结：所有 API Key 都是免费的，不会有任何费用！**

---

## 推荐配置

### 方案 A：零配置（推荐个人项目）

```bash
# 无需任何 Secrets
# 系统使用 fallback 数据正常运行
```

**优点：** 简单，无需管理 Keys  
**缺点：** 新模型发现可能延迟

---

### 方案 B：部分配置（推荐）

```bash
OPENROUTER_API_KEY=sk-or-v1-...  # 只设置这一个！
```

**优点：** 获取 30+ 最新免费模型  
**缺点：** 需要注册 OpenRouter 账号

---

### 方案 C：完整配置（生产环境）

```bash
OPENROUTER_API_KEY=sk-or-v1-...
NOVITA_API_KEY=novita-...
KILOCODE_API_KEY=kilo-...
```

**优点：** 实时获取所有厂商最新数据  
**缺点：** 需要注册 3 个账号**

---

## 下一步

设置完成后，工作流会：
- ✅ 每 3 天自动运行
- ✅ 自动检测模型变化
- ✅ 自动创建 Pull Request
- ✅ 保持数据库最新

🎉 设置完成！
