# 文档工具

`build_stat_report.py` 用于从脚本重新生成需求调研统计报告：

```powershell
python -m pip install -r requirements-docs.txt
python tools/build_stat_report.py
```

输出位置：`docs/research/学术成果分享平台现成调研统计报告.docx`。

生成后应进行 Word 渲染与逐页视觉检查，再提交更新后的 DOCX。脚本中的统计内容来自已核对的公开研究汇编；修改数据时须同步核查来源与证据边界。

