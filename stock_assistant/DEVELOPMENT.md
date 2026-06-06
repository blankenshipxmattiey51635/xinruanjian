# 开发文档

## 技术栈

- Python 3.11+
- PySide6：Windows 桌面界面
- SQLite：本地数据库
- cryptography：本地 API Key 加密保存
- PyInstaller：生成 exe

## 目录说明

```text
stock_assistant/
├── main.py                  # 程序入口
├── requirements.txt          # Python 依赖
├── install.bat               # 一键安装依赖
├── start.bat                 # 一键启动
├── build.bat                 # PyInstaller 打包
├── app/
│   ├── ui/                   # PySide6 界面
│   ├── services/             # 业务服务
│   ├── data_sources/         # 真实数据源适配器
│   ├── strategies/           # 策略模块
│   ├── ai/                   # AI 模型接口
│   ├── backtest/             # 回测模块
│   ├── trading_sim/          # 模拟交易
│   ├── database/             # SQLite schema 和 DAO
│   ├── alerts/               # 提醒系统
│   └── utils/                # 工具函数
├── data/                     # SQLite 数据库
├── config/                   # 用户配置和加密 Key
├── logs/                     # 日志
├── models/                   # 后续机器学习模型
└── exports/                  # 导出文件
```

## 数据真实性原则

- 禁止随机数据、假数据、示例数据伪装成真实行情。
- 免费接口不可用时，界面必须显示“数据源不可用”或“暂无真实数据”。
- 模拟交易可以使用真实行情模拟成交，但必须明确显示“模拟交易”。
- 第一版不接真实券商下单，券商接口模块后续默认禁用实现。

## 常见问题

### 双击 start.bat 闪退

先双击 `install.bat` 安装依赖。若仍失败，在命令提示符进入项目目录执行：

```bat
python main.py
```

查看错误信息。

### 打包后找不到 exe

打包完成后查看：

```text
dist\StockAssistant\StockAssistant.exe
```

### 为什么没有价格？

当前是第一阶段，仅完成基础框架。第二阶段才会接入真实行情源。未接入真实源前，软件按要求显示“数据源不可用”，不会使用假数据。
