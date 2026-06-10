# 炒股辅助软件原型

这是一个最小可运行的炒股辅助软件脚手架，覆盖你提出的五个核心方向：低延迟行情与新闻、股价/指标展示、策略选股、内置可训练 AI、券商接口。当前实现默认使用模拟行情、模拟新闻和纸面交易，避免在未完成合规、风控和券商认证前发送真实委托。

> 风险提示：本项目是工程原型，不构成投资建议。接入真实行情、新闻、AI 模型和券商前，需要补齐数据授权、交易合规、权限隔离、风控、审计日志和灾备方案。

## 已包含功能

- **实时行情**：`/ws/quotes/{symbols}` 通过 WebSocket 每 2 秒推送一次行情，满足 5 秒内刷新目标的原型验证。
- **行情与指标图**：前端仪表盘展示报价卡片，并用 Canvas 绘制价格、MA5、MA20 和 RSI14 指标。
- **相关新闻**：`/api/news` 返回按股票代码聚合的新闻占位数据，后续可替换为正式新闻供应商。
- **策略选股**：`/api/strategies/run` 支持按价格、成交量、短线动量筛选股票并输出评分与理由。
- **内置可训练 AI**：`/api/ai/train` 训练一个本地 tiny trend baseline，`/api/ai/predict/{symbol}` 输出 buy/hold/sell 信号。
- **券商接口**：`/api/broker/orders` 使用纸面交易适配器，接口形态为后续接入真实券商预留。

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

打开 <http://127.0.0.1:8000> 查看仪表盘。

## 关键 API

| 功能 | 方法与路径 | 说明 |
| --- | --- | --- |
| 健康检查 | `GET /health` | 服务状态 |
| 最新报价 | `GET /api/quotes/{symbol}` | 单只股票最新报价 |
| 指标历史 | `GET /api/indicators/{symbol}?points=120` | 价格、MA5、MA20、RSI14 |
| 新闻 | `GET /api/news?symbol=AAPL&limit=10` | 新闻列表 |
| 策略选股 | `POST /api/strategies/run` | 按规则筛选股票池 |
| 训练 AI | `POST /api/ai/train` | 训练本地趋势模型 |
| AI 预测 | `POST /api/ai/predict/{symbol}` | 根据近期价格预测信号 |
| 下单 | `POST /api/broker/orders` | 纸面交易下单 |
| 实时行情流 | `WS /ws/quotes/AAPL,MSFT,NVDA` | 多股票报价推送 |

## 生产化路线图

### 1. 低延迟行情与新闻

- 抽象 `MarketDataProvider` 和 `NewsProvider`，分别接入授权的实时行情源、Level 1/Level 2 行情、交易所延迟行情和新闻源。
- 使用 WebSocket/SSE 推送，后端内部使用异步队列、批量订阅、限流和断线重连。
- 为每条行情记录服务端接收时间、供应商时间、推送时间，持续监控端到端延迟。

### 2. 股价显示与指标

- 增加 K 线、成交量、MACD、BOLL、VWAP、资金流、盘口、分时图、多周期切换和自定义指标。
- 将当前 Canvas 原型替换为专业图表库或内部渲染引擎，并支持多屏、自选股、预警和板块联动。

### 3. 策略选股

- 增加策略 DSL、因子库、回测、交易成本模型、组合约束、风控规则和结果归因。
- 区分研究环境与生产环境，所有策略发布前必须有回测报告、模拟盘验证和审批记录。

### 4. 内置可训练 AI

- 将 tiny baseline 升级为可配置训练流水线：数据清洗、特征工程、训练、验证、模型注册、在线推理和漂移监控。
- AI 输出必须包含置信度、解释、适用范围和风险提示，不应直接绕过风控自动下单。

### 5. 券商接口

- 先保持纸面交易，再接入真实券商 API；生产下单必须实现身份认证、账户权限、订单幂等、风控拦截、审计日志和紧急停止。
- 建议先做只读账户与模拟盘，再逐步开放小额度真实交易。

## 项目结构

```text
app/
  ai/              本地可训练 AI baseline
  broker/          纸面交易与券商适配器接口雏形
  providers/       行情与新闻数据源适配器
  static/          原型仪表盘
  strategies/      策略选股引擎
  main.py          FastAPI 入口与 API 路由
tests/             API 与业务逻辑测试
```
