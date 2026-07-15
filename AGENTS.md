# Temporal Impact — AGENTS.md

## 1. 项目身份

本项目名称：

```text
Temporal Impact
```

项目定位：

> 一个可嵌入现有应用的、事件驱动的动态影响分析引擎。

核心职责：

```text
接收宿主事件
→ 维护影子依赖图
→ 传播变化影响
→ 增量重算观测值
→ 生成可解释 Proposal
```

本项目不替代宿主项目原有的：

```text
数据库
领域模型
任务系统
版本系统
业务服务
工作流
```

---

## 2. 权威文档

开始任何任务前，必须阅读：

```text
AGENTS.md
docs/DEVELOPMENT.md
```

如果存在以下文件，也应读取与当前任务相关的内容：

```text
README.md
docs/EVENT_SCHEMA.md
docs/ADAPTER_GUIDE.md
docs/ALGORITHM.md
docs/INTEGRATION_GUIDE.md
docs/ROADMAP.md
```

优先级：

```text
用户当前明确要求
> AGENTS.md
> docs/DEVELOPMENT.md
> 其他项目文档
> 现有代码推断
```

如果文档和代码冲突：

1. 不得擅自大规模重构；
2. 先报告冲突；
3. 优先保持兼容；
4. 只做当前 Goal 必需的最小修改；
5. 将需要用户决定的问题记录到完成报告。

---

## 3. Goal 模式工作规则

每次只完成一个 Goal。

不得在同一个 Goal 中同时跨越多个阶段。

开始 Goal 前必须：

1. 阅读本文件；
2. 阅读 `docs/DEVELOPMENT.md`；
3. 检查当前 Git 状态；
4. 检查已有代码和测试；
5. 明确本次 Goal 的边界；
6. 列出准备修改的模块；
7. 识别是否存在用户未提交修改；
8. 不覆盖与本 Goal 无关的改动。

执行 Goal 时必须：

1. 只修改必要文件；
2. 不实现下一 Goal；
3. 不引入未批准技术；
4. 为新增核心逻辑添加测试；
5. 保持向后兼容；
6. 所有影响结果必须可解释；
7. 所有事件必须可追踪；
8. 所有 Proposal 必须可追踪来源；
9. 不允许 AI 直接写正式状态；
10. 默认只读，不主动回写宿主系统。

完成 Goal 后必须：

1. 运行相关测试；
2. 运行完整测试；
3. 运行静态检查；
4. 验证 CLI、API 或 UI 中与本 Goal 相关的入口；
5. 报告修改文件；
6. 报告测试命令和结果；
7. 对照验收标准逐项检查；
8. 报告已知限制；
9. 报告未完成项；
10. 停止，不自动开始下一个 Goal；
11. 不执行 `git push`；
12. 未经要求不创建 Git commit。

---

## 4. Goal 完成状态

只能使用：

```text
COMPLETED
PARTIAL
BLOCKED
FAILED
```

不得使用：

```text
基本完成
应该可以
理论上可行
大致完成
```

只有同时满足以下条件才可标记为 `COMPLETED`：

```text
代码已实现
测试已通过
入口可操作
数据可持久化
验收场景可复现
没有越过 Goal 边界
已输出完成报告
```

---

## 5. 技术栈

v0.1 使用：

```text
Python 3.12+
Pydantic
NetworkX
SQLModel
SQLite
Typer
FastAPI
Uvicorn
Streamlit
pytest
ruff
mypy
```

未经用户明确批准，不得引入：

```text
Neo4j
PostgreSQL
Redis
Celery
Dramatiq
Temporal
LangGraph
Graphiti
Salsa
Docker
Kubernetes
微服务
图神经网络
强化学习
复杂多 Agent
```

这些技术可以在后续版本评估，但不得提前加入 v0.1。

---

## 6. 仓库结构

目标结构：

```text
temporal-impact/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── src/
│   └── temporal_impact/
│       ├── events/
│       ├── shadow/
│       ├── graph/
│       ├── impact/
│       ├── observations/
│       ├── proposals/
│       ├── adapters/
│       ├── storage/
│       ├── api/
│       ├── cli/
│       └── demo/
├── examples/
├── docs/
├── tests/
└── .github/
```

允许小幅调整，但必须保持以下模块边界：

```text
事件接收
影子对象
图构建
影响传播
观测计算
Proposal
Adapter
存储
API
CLI
Demo
```

---

## 7. 宿主项目原则

### 7.1 唯一事实来源

宿主项目是唯一事实来源。

Temporal Impact 不得保存第二套完整业务数据。

允许保存：

```text
宿主对象引用
对象类型
对象 ID
修订号
哈希
摘要
关系
观测值
影响结果
Proposal
```

禁止保存：

```text
完整章节正文
完整代码文件副本
完整论文正文副本
宿主认证信息
无必要的敏感数据
```

### 7.2 影子对象

所有业务对象在本项目中必须表示为：

```text
ShadowNode
ShadowRelation
```

不得将宿主业务对象直接复制为本项目正式模型。

### 7.3 默认只读

v0.1 默认流程：

```text
观察
→ 分析
→ 生成 Proposal
```

不得自动：

```text
修改宿主数据
删除宿主对象
创建宿主任务
重写宿主内容
```

回写只能通过 `HostAdapter.apply_proposal()`，且必须由用户明确确认。

---

## 8. 事件原则

所有变化通过标准 `ChangeEvent` 进入系统。

v0.1 支持：

```text
object.created
object.updated
object.deleted
relation.changed
task.completed
```

每个事件至少包含：

```text
event_id
event_type
source
project_id
branch_id
object reference
before
after
occurred_at
metadata
```

### 8.1 幂等性

同一个 `event_id` 重复提交时：

```text
不重复保存事件
不重复生成报告
不重复生成 Proposal
```

### 8.2 时间

`occurred_at` 必须带时区。

禁止使用无时区时间作为正式事件时间。

---

## 9. 影子图原则

### 9.1 ShadowNode

至少包含：

```text
id
project_id
branch_id
source_system
source_type
source_id
source_revision
fingerprint
summary
importance
status
```

状态：

```text
valid
possibly_affected
conflict
stale
discarded
locked
```

### 9.2 ShadowRelation

至少包含：

```text
source_node_id
target_node_id
relation_type
weight
confidence
status
evidence
```

### 9.3 图算法

核心图算法必须独立于：

```text
Streamlit
FastAPI
CLI
SQLite 具体实现
```

界面层不得包含传播算法。

---

## 10. 影响传播原则

v0.1 使用：

```text
受限 BFS
关系权重
距离衰减
节点重要度
关系置信度
```

默认最大深度：

```text
3
```

影响分数至少考虑：

```text
ChangeStrength
× RelationWeight
× DistanceDecay
× TargetImportance
× Confidence
```

每个影响结果必须保存：

```text
目标节点
影响分数
影响等级
传播距离
完整传播路径
每条边类型
每条边权重
原因
```

必须正确处理：

```text
图中环
多路径
失效关系
锁定节点
无关系节点
重复事件
深度限制
```

不得只返回一个无法解释的数值。

---

## 11. 观测值原则

v0.1 包含：

```text
conflict_score
staleness_score
stability_score
```

每个观测值必须保存：

```text
目标
当前值
前一个值
依赖
状态
计算版本
来源事件
计算时间
```

### 11.1 增量重算

变化发生后：

```text
查找受影响依赖
→ 标记 dirty
→ 只重算 dirty 观测
→ 未受影响结果继续复用
```

禁止每次事件都无条件重算全部项目。

---

## 12. Proposal 原则

Proposal 是建议，不是正式业务修改。

v0.1 类型：

```text
review_required
mark_stale
create_revision_task
branch_recommended
recalculate_required
```

状态：

```text
pending
accepted
rejected
applied
obsolete
```

每个 Proposal 必须保存：

```text
来源事件
目标对象
建议类型
优先级
原因
证据
状态
所属项目
所属分支
```

禁止：

```text
Proposal 创建后自动回写宿主
重复创建相同 Proposal
已过期 Proposal 继续执行
```

---

## 13. Adapter 原则

`HostAdapter` 是接入现有项目的唯一正式接口。

至少提供：

```python
get_object()
list_relations()
```

可选提供：

```python
apply_proposal()
```

Adapter 必须：

```text
隔离宿主实现细节
不泄漏宿主数据库结构
不绕过宿主 Service
不直接写宿主数据库
```

测试必须使用：

```text
MemoryAdapter
FakeAdapter
MockAdapter
```

不得依赖真实第三方项目才能通过测试。

---

## 14. SDK 原则

公开 SDK 必须简单。

核心导入：

```python
from temporal_impact import (
    ImpactEngine,
    ChangeEvent,
    ShadowNode,
    ShadowRelation,
    ImpactReport,
)
```

核心方法：

```text
register_node
register_relation
ingest
analyze
get_report
list_proposals
```

公开 API 必须稳定、带类型注解和文档字符串。

内部实现不得通过大量私有依赖泄漏到公共接口。

---

## 15. API 原则

Sidecar API 使用 FastAPI。

v0.1 至少提供：

```text
GET  /health
POST /events
POST /analyze
GET  /reports/{report_id}
GET  /projects/{project_id}/graph
GET  /projects/{project_id}/proposals
POST /proposals/{proposal_id}/accept
```

要求：

```text
统一错误结构
明确 HTTP 状态码
OpenAPI 可用
输入使用 Pydantic 校验
不返回 Python 堆栈给普通用户
```

v0.1 不实现：

```text
认证
多租户
云部署
支付
远程账户
```

---

## 16. CLI 原则

CLI 使用 Typer。

命令：

```text
init
ingest
analyze
graph
proposals
serve
demo
```

错误信息必须便于小白理解。

禁止直接把完整异常堆栈作为默认用户输出。

调试模式可以提供详细堆栈。

---

## 17. Demo 原则

Demo 使用 Streamlit。

页面：

```text
Overview
Event Timeline
Shadow Graph
Impact Report
Observations
Proposals
```

必须内置：

```text
师父死亡 → 师父假死
```

固定演示不得依赖：

```text
真实 AI
外部 API
互联网
Neo4j
```

必须支持：

```text
一键加载演示
一键应用变更
一键重置
```

---

## 18. 编码规则

- 使用完整类型注解；
- 使用 Pydantic 或 SQLModel 校验；
- 函数职责单一；
- 避免超大文件；
- 避免循环依赖；
- 不复制业务逻辑；
- repository 负责持久化；
- service/engine 负责业务逻辑；
- UI 不直接访问数据库；
- 核心算法不直接依赖 UI；
- 不硬编码绝对路径；
- Windows、macOS、Linux 路径兼容；
- 不在代码中保存 API Key；
- 不提交本地数据库；
- 不提交虚拟环境和缓存；
- 公共类和复杂函数必须有 docstring；
- 关键算法添加简短中文或英文注释；
- 错误信息应面向普通开发者，而非只面向作者本人。

---

## 19. 测试规则

必须包含：

```text
unit
integration
end_to_end
```

至少测试：

```text
事件验证
事件幂等
SQLite 持久化
关系权重
距离衰减
环检测
多路径
深度限制
影响等级
观测增量重算
Proposal 去重
Proposal 失效
SDK 使用
API 使用
CLI 使用
Demo 启动
```

固定端到端场景：

```text
师父死亡
→ 师父假死
→ 第12章冲突度上升
→ 第20章过期度上升
→ 稳定度下降
→ Proposal 生成
```

测试原则：

```text
不调用真实 AI
使用临时 SQLite
测试互相隔离
不依赖执行顺序
不得隐藏失败
不得通过 skip 掩盖缺陷
```

---

## 20. 数据库规则

- 初始化必须可重复执行；
- 测试数据库不得污染正式数据库；
- 数据库路径由统一配置管理；
- 不要求用户手动删除数据库才能升级；
- schema 变化必须同步测试；
- 不物理删除历史事件；
- 业务删除优先使用状态标记；
- 数据库写入必须有事务边界；
- 事件、报告和 Proposal 不得出现半成功状态。

---

## 21. Git 规则

禁止：

```text
git push
git reset --hard
强制覆盖用户修改
删除用户提交
修改远程仓库
```

每个 Goal 完成后必须报告：

```text
git status
git diff --stat
```

只有用户明确要求时才能创建 commit。

发现工作区存在不属于当前 Goal 的修改时：

1. 不覆盖；
2. 不撤销；
3. 在报告中说明；
4. 仅修改当前 Goal 必需文件。

---

## 22. 禁止事项

未经明确批准，不得：

- 开始下一 Goal；
- 扩大 v0.1 范围；
- 自动修改宿主项目；
- 保存宿主完整业务数据；
- 强制接入 AI；
- 强制使用图数据库；
- 添加用户系统；
- 添加云同步；
- 添加多人协作；
- 添加支付；
- 添加四维球体；
- 添加复杂动画；
- 添加多 Agent；
- 更换主要技术栈；
- 大规模重构；
- 删除历史事件；
- 隐藏测试失败；
- 自动发布 PyPI；
- 自动创建 GitHub Release。

---

## 23. Goal 完成报告格式

每次完成后必须按以下格式输出：

```markdown
# Goal 完成报告

## Goal
本次目标。

## 状态
COMPLETED / PARTIAL / BLOCKED / FAILED

## 已完成
- ...

## 修改文件
- ...

## 数据库变化
- ...

## 公共接口变化
- ...

## 测试
- 命令：
- 结果：

## 静态检查
- ruff：
- mypy：

## 启动验证
- CLI：
- API：
- Demo：

## 验收标准
- [x] ...
- [ ] ...

## 已知限制
- ...

## 未解决问题
- ...

## Git 状态
- git status：
- git diff --stat：

## 下一步建议
只说明推荐的下一个 Goal，不得自动开始。
```

---

## 24. v0.1 最终验收

必须全部满足：

```text
[ ] pip install -e . 成功
[ ] temporal-impact --help 成功
[ ] temporal-impact demo 成功
[ ] temporal-impact serve 成功
[ ] 师父假死演示成功
[ ] 软件开发示例成功
[ ] 论文示例成功
[ ] 重复事件不重复处理
[ ] 图中有环时不会死循环
[ ] 多路径处理正确
[ ] 影响报告显示完整路径
[ ] 观测值会动态变化
[ ] 无关观测不会重算
[ ] Proposal 不直接改宿主
[ ] Proposal 不重复创建
[ ] SQLite 重启后数据保留
[ ] pytest 全部通过
[ ] ruff 通过
[ ] mypy 通过
[ ] GitHub Actions 通过
[ ] README 10 分钟内可跑通
```

---

## 25. 最终原则

Temporal Impact 必须始终保持：

```text
容易安装
容易演示
容易嵌入
默认只读
输出可解释
不替代宿主系统
不强制 AI
```

v0.1 最重要的成功标准：

> 一个陌生开发者能在 10 分钟内启动 Demo，并在 30 分钟内通过一个 JSON 事件接入自己的项目。
