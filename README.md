# SFM 1.0 - Serenity Football Model

[中文说明](#中文说明) | [English](#english)

* * *

## 中文说明

SFM（Serenity Football Model）是一个本地足球比赛概率预测系统。它的目标不是做一个简单表格，而是搭建一套可以长期迭代的量化足球预测框架：数据更新、球队数据库、概率模型、赔率 Value、校准评估和 Dashboard 都放在一个清晰的 Python 项目里。

当前版本是 **SFM 1.0 原型版**，已经可以完成：

* 读取球队基础数据 `teams.csv`
* 读取比赛数据 `matches.csv`
* 根据 Elo、攻防强度、门将强度、Momentum 计算进球期望值 lambda
* 使用双泊松模型生成胜 / 平 / 负概率
* 输出最可能比分
* 根据赔率计算 Value Index
* 生成预测结果 CSV
* 生成本地 HTML Dashboard
* 支持数据更新配置
* 支持 football-data.org 和 The Odds API 的接口模板
* 支持作为 Python 库发布到 GitHub

> 重要说明：这是研究和建模项目，不是投注建议。模型输出是概率估计，不能保证结果。

* * *

## 项目结构

    SFM/
      .github/
        workflows/
          tests.yml
      config/
        data_sources.json
      data/
        live/
          .gitkeep
        sample/
          matches.csv
          teams.csv
      docs/
        DATA_SOURCES.md
        GITHUB_RELEASE.md
      scripts/
        run_demo.py
        update_data.py
      sfm_engine/
        __init__.py
        calibration.py
        cli.py
        dashboard.py
        data_io.py
        elo.py
        models.py
        monte_carlo.py
        poisson.py
        predictor.py
        updater.py
      tests/
        test_engine.py
      .gitignore
      LICENSE
      README.md
      setup.cfg
      setup.py

核心目录说明：

* `sfm_engine/`：模型和数据更新的核心代码
* `data/sample/`：示例数据，可以直接运行
* `data/live/`：实时更新数据的输出目录
* `config/data_sources.json`：数据源配置
* `outputs/`：预测结果和 Dashboard 输出目录，运行后自动生成
* `docs/`：数据源和 GitHub 发布说明
* `tests/`：自动化测试

* * *

## 从零开始使用

以下命令以 Windows PowerShell 为例。

### 1. 进入项目目录

    cd "D:\your project"

命令行前面应该类似：

    PS D:\your project>

如果你还在 `C:\Users\admin`，说明还没有进入项目目录。

### 2. 创建虚拟环境

    py -3.9 -m venv .venv

这个命令会在项目目录下创建 `.venv` 文件夹。它是项目自己的 Python 环境，不需要上传到 GitHub。

### 3. 激活虚拟环境

    .\.venv\Scripts\Activate.ps1

激活成功后，命令行前面会出现：

    (.venv) PS D:\New project>

### 4. 安装本地库

    python -m pip install -e .

安装完成后，你就可以使用 `sfm` 命令。

### 5. 更新数据

    sfm update

默认情况下，它会读取 `config/data_sources.json`，把示例数据更新到：

    data/live/

当前默认生成：

    data/live/teams.csv
    data/live/matches.csv

### 6. 运行预测

    sfm predict --data-dir data\live

运行后会生成：

    outputs/predictions.csv
    outputs/dashboard.html

### 7. 查看 Dashboard

打开：

    outputs/dashboard.html

你可以直接双击这个文件，或者在浏览器里打开。

* * *

## 最常用命令

每次重新打开 PowerShell 后，通常只需要：

    cd "D:\your project"
    .\.venv\Scripts\Activate.ps1
    sfm update
    sfm predict --data-dir data\live

如果只是快速跑示例，也可以：

    py -3.9 scripts\run_demo.py

* * *

## 输入数据格式

### 球队数据：`teams.csv`

位置：

    data/sample/teams.csv
    data/live/teams.csv

字段：

    team,elo,attack_strength,defense_weakness,keeper_strength,penalty_strength,momentum
    Argentina,2145,1.18,0.86,1.08,1.12,0.08
    France,2110,1.21,0.91,1.03,1.06,0.06

字段含义：

* `team`：球队名称
* `elo`：球队 Elo 评分
* `attack_strength`：进攻强度，通常 1.00 为平均水平
* `defense_weakness`：防守弱点系数，越高代表越容易丢球
* `keeper_strength`：门将强度，越高代表越能降低对方进球期望
* `penalty_strength`：点球能力，后续点球模块会使用
* `momentum`：近期状态，正数代表状态较好，负数代表状态较差

### 比赛数据：`matches.csv`

位置：

    data/sample/matches.csv
    data/live/matches.csv

字段：

    match_id,date,home_team,away_team,neutral_site,home_odds,draw_odds,away_odds
    M001,2026-06-30,Argentina,France,true,2.55,3.20,2.85

字段含义：

* `match_id`：比赛 ID
* `date`：比赛日期，格式建议使用 `YYYY-MM-DD`
* `home_team`：主队或名义主队
* `away_team`：客队或名义客队
* `neutral_site`：是否中立场，世界杯通常为 `true`
* `home_odds`：主胜赔率
* `draw_odds`：平局赔率
* `away_odds`：客胜赔率

* * *

## 输出结果

### `outputs/predictions.csv`

预测结果包含：

* `match_id`
* `date`
* `home_team`
* `away_team`
* `home_lambda`
* `away_lambda`
* `home_win_prob`
* `draw_prob`
* `away_win_prob`
* `most_likely_score`
* `value_home`
* `value_draw`
* `value_away`

其中：

* `home_lambda` / `away_lambda` 是双方进球期望值
* `home_win_prob` / `draw_prob` / `away_win_prob` 是胜平负概率
* `most_likely_score` 是双泊松矩阵里概率最高的比分
* `value_*` 是模型概率和市场赔率之间的差值指标

### `outputs/dashboard.html`

这是本地 Dashboard，展示每场比赛的：

* 比赛日期
* 对阵双方
* lambda
* 胜平负概率
* 最可能比分
* 最佳 Value

* * *

## 数据自动更新

数据源配置文件：

    config/data_sources.json

当前支持：

* `local_csv`：复制本地 CSV
* `http_csv`：下载在线 CSV
* `football_data_org_teams`：从 football-data.org 获取球队
* `football_data_org_matches`：从 football-data.org 获取赛程 / 赛果
* `the_odds_api_h2h`：从 The Odds API 获取胜平负赔率

默认配置里，真实 API 模板已经写好，但设置为：

    "enabled": false

如果你要启用真实数据，把对应数据源改成：

    "enabled": true

然后设置 API Key。

### 设置 football-data.org Key

PowerShell：

    $env:FOOTBALL_DATA_API_KEY="你的football-data.org key"

### 设置 The Odds API Key

PowerShell：

    $env:ODDS_API_KEY="你的The Odds API key"

然后运行：

    sfm update
    sfm predict --data-dir data\live

更详细的数据源说明见：

    docs/DATA_SOURCES.md

* * *


## 测试

运行测试：

    python -m unittest discover -s tests

如果使用虚拟环境：

    .\.venv\Scripts\python -m unittest discover -s tests

当前测试覆盖：

* 预测概率是否归一
* Brier Score / Log Loss
* 本地 CSV 更新
* football-data.org 数据转换
* The Odds API 赔率转换和合并

* * *

## 常见问题

### PowerShell 提示找不到 `sfm`

通常是没有进入项目目录，或者没有激活项目虚拟环境。

正确顺序：

    cd "D:\New project"
    .\.venv\Scripts\Activate.ps1
    sfm update

如果还是不行，使用完整路径：

    .\.venv\Scripts\sfm.exe update

### `sfm update` 没有拉取真实数据

检查：

* `config/data_sources.json` 里的真实 API 源是否是 `"enabled": true`
* 是否设置了 API Key
* API Key 名称是否对应 `api_key_env`

### 真实 API 返回的球队名和样例球队名不一致怎么办？

真实数据源经常有命名差异，例如 `USA`、`United States`、`United States of America`。后续建议加入 `team_aliases.csv` 做球队名称映射。

### xG、伤病和预计首发能自动更新吗？

可以设计接口，但免费稳定数据源较少。通常需要专业数据供应商。当前版本先把赛程、球队和赔率接口打通，xG / 伤病 / 首发适合放在 SFM 1.1 或 SFM 1.2。

* * *

## Roadmap

* SFM 1.0：本地概率预测模型
* SFM 1.1：真实赛程、赔率、赛果自动更新
* SFM 1.2：晋级概率、点球概率、Monte Carlo 深化
* SFM 2.0：模型校准、自动权重优化、历史回测
* SFM 3.0：支持世界杯、欧冠、五大联赛、美洲杯、欧洲杯统一预测

* * *

## English

SFM, short for Serenity Football Model, is a local football probabilityprediction system. It is designed as a long-term quantitative football analyticsproject rather than a spreadsheet-only tracker.

The current version is **SFM 1.0 Prototype**. It can:

* Read team ratings from `teams.csv`
* Read match inputs from `matches.csv`
* Estimate expected goals with Elo, attack strength, defensive weakness,goalkeeper strength, and momentum
* Generate win/draw/loss probabilities with a double Poisson model
* Output the most likely scoreline
* Compute a simple market Value Index from odds
* Write prediction results to CSV
* Generate a local HTML dashboard
* Refresh data from configurable sources
* Provide connector templates for football-data.org and The Odds API
* Be packaged and published as a Python library on GitHub

> Note: SFM is a research and modeling project. It is not betting advice.

* * *

## Project Layout

    SFM/
      .github/
        workflows/
          tests.yml
      config/
        data_sources.json
      data/
        live/
          .gitkeep
        sample/
          matches.csv
          teams.csv
      docs/
        DATA_SOURCES.md
        GITHUB_RELEASE.md
      scripts/
        run_demo.py
        update_data.py
      sfm_engine/
        __init__.py
        calibration.py
        cli.py
        dashboard.py
        data_io.py
        elo.py
        models.py
        monte_carlo.py
        poisson.py
        predictor.py
        updater.py
      tests/
        test_engine.py
      .gitignore
      LICENSE
      README.md
      setup.cfg
      setup.py

* * *

## Quick Start From Zero

The examples below use Windows PowerShell.

### 1. Enter the project folder

    cd "D:\your project"

### 2. Create a virtual environment

    py -3.9 -m venv .venv

### 3. Activate the virtual environment

    .\.venv\Scripts\Activate.ps1

After activation, the prompt should look like:

    (.venv) PS D:\New project>

### 4. Install the local package

    python -m pip install -e .

This installs the `sfm` command.

### 5. Refresh data

    sfm update

By default, this copies the sample data into:

    data/live/

### 6. Run predictions

    sfm predict --data-dir data\live

This creates:

    outputs/predictions.csv
    outputs/dashboard.html

### 7. Open the dashboard

Open:

    outputs/dashboard.html

You can double-click the file or open it in a browser.

* * *

## Daily Usage

After the project is installed, the normal workflow is:

    cd "D:\your project"
    .\.venv\Scripts\Activate.ps1
    sfm update
    sfm predict --data-dir data\live

For a quick sample run:

    py -3.9 scripts\run_demo.py

* * *

## Input Data

### `teams.csv`

Example:

    team,elo,attack_strength,defense_weakness,keeper_strength,penalty_strength,momentum
    Argentina,2145,1.18,0.86,1.08,1.12,0.08
    France,2110,1.21,0.91,1.03,1.06,0.06

Columns:

* `team`: team name
* `elo`: team Elo rating
* `attack_strength`: attacking strength, where 1.00 is roughly average
* `defense_weakness`: defensive weakness, where higher means more vulnerable
* `keeper_strength`: goalkeeper strength
* `penalty_strength`: penalty ability for future penalty modules
* `momentum`: recent form adjustment

### `matches.csv`

Example:

    match_id,date,home_team,away_team,neutral_site,home_odds,draw_odds,away_odds
    M001,2026-06-30,Argentina,France,true,2.55,3.20,2.85

Columns:

* `match_id`: match identifier
* `date`: match date, preferably `YYYY-MM-DD`
* `home_team`: home or nominal home team
* `away_team`: away or nominal away team
* `neutral_site`: whether the match is played on neutral ground
* `home_odds`: home win odds
* `draw_odds`: draw odds
* `away_odds`: away win odds

* * *

## Outputs

### `outputs/predictions.csv`

Includes:

* match date
* teams
* expected goals
* win/draw/loss probabilities
* most likely scoreline
* Value Index

### `outputs/dashboard.html`

Local dashboard showing:

* match date
* teams
* expected goals
* probability bars
* most likely score
* best value candidate

* * *

## Data Updates

Data sources are configured in:

    config/data_sources.json

Supported source types:

* `local_csv`: copy a local CSV file
* `http_csv`: download a CSV file from an HTTP endpoint
* `football_data_org_teams`: fetch teams from football-data.org
* `football_data_org_matches`: fetch fixtures/results from football-data.org
* `the_odds_api_h2h`: fetch 1X2 odds from The Odds API

Real API sources are included as templates with:

    "enabled": false

To activate a real source, change it to:

    "enabled": true

Then set API keys:

    $env:FOOTBALL_DATA_API_KEY="your-football-data-key"
    $env:ODDS_API_KEY="your-odds-api-key"
    sfm update

More details:

    docs/DATA_SOURCES.md

* * *


## Tests

Run:

    python -m unittest discover -s tests

Or:

    .\.venv\Scripts\python -m unittest discover -s tests

* * *

## Roadmap

* SFM 1.0: local probability model
* SFM 1.1: real fixtures, odds, and result updates
* SFM 1.2: qualification paths, penalties, and deeper Monte Carlo simulation
* SFM 2.0: calibration, automatic weight tuning, and backtesting
* SFM 3.0: World Cup, Champions League, top domestic leagues, Copa America,and European Championship support

如果对你有帮助，可以支持一下
<img width="75.7" height="82.8" alt="微信图片_20260630140933_21_2" src="https://github.com/user-attachments/assets/73bf9609-7a4b-4a80-8765-6eb23b98b2e0" />

