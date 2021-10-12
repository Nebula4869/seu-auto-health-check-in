# 东南大学每日健康上报自动化脚本

## Environments

Only test on Windows 10, not support on Linux/Mac.

Google Chrome

Python==3.7.0

func_timeout==4.3.5

requests==2.24.0

selenium==3.141.0

## Getting started

### Configure Environment

```shell
pip install -r requirements.txt -i https://pypi.douban.com/simple
```

### Run with python/pythonw

```shell
pythonw main.py check_in_time(09:30:00) username(220190785) password(123456) bbt(36.2)
```

Then the program will perform health check-in at 09:30:00 every day (please make sure the program is running at that time), with pythonw you can hide the background
