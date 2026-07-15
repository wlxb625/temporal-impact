# Temporal Impact

[English README](README.md)

一个可嵌入现有应用的、事件驱动的动态影响分析引擎。

Temporal Impact 接收宿主系统的变化事件，维护影子依赖图，计算可解释的影响范围，并生成仅供人工处理的 Proposal（建议）。它默认只读：宿主项目始终是唯一事实来源。

> 当前版本：`v0.1.0-alpha`。已提供本地 SDK、CLI、FastAPI Sidecar 与 Streamlit 演示。

## 适用场景

- 小说设定调整：师父死亡改为师父假死，哪些章节需要复核？
- 软件变更：删除 API 字段后，哪些前端类型、测试和文档会受影响？
- 研究调整：样本区间变化后，哪些统计表、回归结果与摘要数字可能过期？

## 快速安装

要求 Python 3.12 或更高版本。

```bash
git clone https://github.com/<你的用户名>/temporal-impact.git
cd temporal-impact
python -m pip install -e ".[dev]"
```

检查安装：

```bash
temporal-impact --help
```

## 10 分钟体验：师父假死 Demo

```bash
temporal-impact demo
```

浏览器打开 Streamlit 页面后：

1. 点击“加载演示”。
2. 点击“应用：师父假死”。
3. 在 Impact Report、Observations、Proposals 页面查看完整影响路径、分数和建议。

演示完全离线，不调用 AI、互联网或任何宿主系统，也不会回写数据。

## 最小 SDK 示例

```python
from temporal_impact import ChangeEvent, ImpactEngine, ShadowNode, ShadowRelation

engine = ImpactEngine(database_url="sqlite:///impact.db")
engine.register_node(
    ShadowNode(
        id="master",
        project_id="novel",
        source_system="novel-app",
        source_type="character",
        source_id="master",
    )
)
engine.register_node(
    ShadowNode(
        id="chapter-12",
        project_id="novel",
        source_system="novel-app",
        source_type="chapter",
        source_id="12",
    )
)
engine.register_relation(
    ShadowRelation(
        id="master-conflicts-chapter-12",
        project_id="novel",
        source_node_id="master",
        target_node_id="chapter-12",
        relation_type="conflicts_with",
        weight=0.94,
    )
)

event = ChangeEvent.model_validate(
    {
        "event_id": "master-alive",
        "event_type": "object.updated",
        "source": "novel-app",
        "project_id": "novel",
        "object": {"type": "character", "id": "master"},
        "before": {"status": "dead"},
        "after": {"status": "hidden_alive"},
        "occurred_at": "2026-07-15T10:30:00+08:00",
    }
)
report = engine.analyze(event)
print(report.impacts)
```

每项影响结果都包含目标节点、影响分数、等级、传播距离、完整边路径和原因。

## CLI

```bash
temporal-impact init
temporal-impact ingest event.json
temporal-impact analyze event.json
temporal-impact graph <project_id>
temporal-impact proposals <project_id>
temporal-impact serve
temporal-impact demo
```

`serve` 默认启动在 `http://127.0.0.1:8765`，OpenAPI 文档位于 `/docs`。

## Sidecar API

| 方法 | 地址 | 作用 |
| --- | --- | --- |
| GET | `/health` | 健康检查 |
| POST | `/events` | 验证并保存事件 |
| POST | `/analyze` | 分析事件并生成报告 |
| GET | `/reports/{report_id}` | 读取报告 |
| GET | `/projects/{project_id}/graph` | 读取影子图 |
| GET | `/projects/{project_id}/proposals` | 列出建议 |
| POST | `/proposals/{proposal_id}/accept` | 仅更新本地建议状态 |

## 核心能力

- 五种标准事件：创建、更新、删除、关系变更、任务完成。
- SQLite 持久化与 `event_id` 幂等。
- 受限 BFS（最大深度 3）、权重、置信度、重要度和距离衰减。
- 环、多路径、失效关系、锁定节点的安全处理。
- `conflict_score`、`staleness_score`、`stability_score` 的增量重算。
- 可追溯 Proposal：不会自动写回宿主系统。

## 示例

- [小说：师父假死](examples/novel_adapter)
- [软件：删除 currency 字段](examples/software_change)
- [研究：修改样本年份](examples/research_change)

三个示例均使用同一个 `ImpactEngine`，可以直接运行各目录中的 `example.py`。

## 接入原则

1. 宿主项目保存真实业务数据；Temporal Impact 只保存引用、摘要、哈希和分析结果。
2. 通过 `HostAdapter` 接入宿主的对象和关系读取能力。
3. 先让系统观察和生成 Proposal；仅在用户明确确认后，宿主系统才可自行回写。

## 文档

- [事件协议](docs/EVENT_SCHEMA.md)
- [Adapter 接入指南](docs/ADAPTER_GUIDE.md)
- [影响传播算法](docs/ALGORITHM.md)
- [集成指南](docs/INTEGRATION_GUIDE.md)
- [发布检查表](docs/RELEASE_CHECKLIST.md)

## 开发与质量检查

```bash
pytest
ruff check .
mypy src
```

## 许可证

本项目采用 [Apache License 2.0](LICENSE)。
