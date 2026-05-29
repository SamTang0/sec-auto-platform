# 安全自动化平台

安全告警监控、资产发现、IP威胁情报查询、WAF日志分析一体化工具。

## 安装

```bash
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 ORCA_AUTH_TOKEN
```

## 使用方法

```bash
# 启动监控（告警+资产）
python scripts/run_orca_monitor.py

# IP威胁情报查询
python scripts/run_threat_intel.py -f ips.txt

# WAF日志分析
python scripts/run_waf_analyzer.py

# URL资产匹配
python scripts/run_url_matcher.py url.txt
```

## 配置说明

环境变量 说明
ORCA_AUTH_TOKEN Orca Security Token（必需）
WEBHOOK_URL 企业微信/钉钉推送地址（可选）
AWS_PROFILE AWS CLI配置（WAF分析需要）

## 输出

· 告警/资产数据导出到 reports/ 目录
· 日志保存在 logs/ 目录
· 支持Excel报告和Webhook推送

## 停止运行

按 Ctrl + C
