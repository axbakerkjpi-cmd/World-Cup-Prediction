# World-Cup-Prediction
SFM（Serenity Football Model）是一个以概率预测为核心的足球比赛分析模型。  本项目借鉴量化投资和科研建模的思想，不追求预测每一场比赛，而是希望建立一个长期可校准、可迭代、可验证的概率模型。/ SFM is a local football prediction system. The first version focuses on a clear,auditable prediction engine, configurable data updates, and a package structurethat can be published on GitHub.
What is included

* Team rating database in CSV form
* Match input database in CSV form
* Elo-adjusted attacking expectation
* Double Poisson score matrix
* Win/draw/loss probabilities
* Simple market value index
* Brier score and log-loss helpers
* Monte Carlo simulation helper
* Local HTML dashboard generator
* Configurable data updater for local CSV and HTTP CSV sources
* Python package metadata and CLI entry point

# SFM (Serenity Football Model)

## 项目简介

SFM（Serenity Football Model）是一个以**概率预测**为核心的足球比赛分析模型。

本项目借鉴量化投资和科研建模的思想，不追求预测每一场比赛，而是希望建立一个**长期可校准、可迭代、可验证**的概率模型。

模型主要应用于：

* 世界杯
---

# 项目目标

SFM 不回答：

> **"谁一定会赢？"**

而回答：

> **"哪支球队获胜的概率更高？市场是否存在定价偏差？"**

最终输出包括：

* 90 分钟胜 / 平 / 负概率
* 晋级概率
* 最可能比分
* 冷门指数
* Confidence（预测可信度）
* Value Index（模型概率与市场概率偏差）

---

# 核心思想

SFM 采用多模型融合，而非依赖单一指标。

目前版本包括：

1. Elo（长期实力）
2. 本届赛事表现（攻防效率）
3. 贝叶斯更新（Bayesian Update）
4. 双泊松比分模型（Double Poisson）
5. 淘汰赛修正（Knockout Adjustment）
6. 市场赔率校准（Market Calibration）

未来版本还将加入：

* Monte Carlo Simulation
* 球员级影响模型
* Expected Threat（xT）
* 机器学习自动校准

---

# 项目结构

```text
SFM/
│
├── Team Database
│      ├── Elo
│      ├── Attack Rating
│      ├── Defense Rating
│      ├── Goalkeeper
│      ├── Momentum
│      └── Coach
│
├── Prediction Engine
│      ├── Bayesian Update
│      ├── Double Poisson
│      ├── Monte Carlo
│      └── Knockout Adjustment
│
├── Market Module
│      ├── Odds
│      ├── Implied Probability
│      └── Value Index
│
├── Validation
│      ├── Brier Score
│      ├── Log Loss
│      └── Calibration Curve
│
└── Dashboard
```

---

# 当前版本

**SFM 1.0（Prototype）**

已完成：

* 数据库框架
* 概率预测框架
* Excel 原型
* 模型校准框架

计划开发：

* Python 自动计算引擎
* 自动更新比赛数据
* 蒙特卡洛模拟
* 自动生成比赛预测报告

---

# 模型验证流程

每场比赛采用统一流程：

1. 赛前更新球队数据
2. 运行模型生成预测
3. 记录真实比赛结果
4. 计算预测误差
5. 更新模型参数

形成持续迭代的闭环：

**Predict → Observe → Validate → Improve**

---

# 长期目标

SFM 的目标不是提高单场命中率，而是建立一个经过统计检验的概率模型，使预测结果长期保持良好的校准能力。

未来希望实现：

* 自动数据更新
* 一键生成预测报告
* 多赛事统一支持
* 本地桌面程序（EXE）
* 可视化 Dashboard
* 长期历史数据库

---

# License

Research Prototype

仅用于学习、研究和数据分析，不构成任何博彩、投资或商业建议。

## Quick start

Use Python 3.9 or newer:

    py -3.9 scripts/run_demo.py

This writes:

* `outputs/predictions.csv`
* `outputs/dashboard.html`

Open `outputs/dashboard.html` in a browser to view the first local dashboard.

## Command line usage

Install the package locally:

    py -3.9 -m pip install -e .

Run predictions:

    sfm predict

Refresh data from configured sources:

    sfm update
    sfm predict --data-dir data/live

Data sources are configured in `config/data_sources.json`. The updater supports:

* `local_csv`: copy a controlled CSV into the live data folder
* `http_csv`: download a live CSV endpoint, optionally with an API key from anenvironment variable

## Project layout

    data/
      live/
      sample/
        teams.csv
        matches.csv
    config/
      data_sources.json
    sfm_engine/
      cli.py
      calibration.py
      dashboard.py
      data_io.py
      elo.py
      models.py
      monte_carlo.py
      poisson.py
      predictor.py
      updater.py
    scripts/
      run_demo.py
      update_data.py
    tests/
      test_engine.py
    outputs/

## Version direction

* SFM 1.0: local probability model for tournament matches
* SFM 1.1: automated data update and odds ingestion
* SFM 1.2: qualification paths, penalties, and deeper simulation
* SFM 2.0: model calibration and machine-learning weight tuning
