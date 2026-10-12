# 文档工具

`build_stat_report.py` 用于重新生成二手统计汇编；`export_course_reports.py` 将需求调研主报告、调研依据台账与核心规则 SPEC 的 Markdown 正文同步导出 Word。SRS 的规范性源稿保留在 `docs/srs/`，按顺序运行：

```powershell
python -m pip install -r requirements-docs.txt
python tools/build_stat_report.py
python tools/build_srs_review.py
python tools/check_srs_quality.py
python tools/export_srs_docx.py
python tools/export_course_reports.py
```

输出位置见 `docs/research/`、`docs/spec/`、`docs/srs/` 对应 README。Word 是导出件；修改正文应先改源稿或相应生成脚本，不要只在 Word 中改动后遗失源稿同步。

生成后应进行 Word 渲染与逐页视觉检查，再提交更新后的 DOCX。Windows 上若统一 `render_docx.py` 因缺少 LibreOffice 无法运行，可使用本机 Word 的 `render_course_reports_windows.py` 和 `render_srs_windows.py` 生成 `.local/` 下的 PDF、页面图与联系表；这些 QA 文件不进入课程交付。脚本中的统计数据须同步核查原始来源、分母与证据边界。

