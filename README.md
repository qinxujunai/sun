# Sun · 认知决策助手

把增长视角与生活决策证据放在一起，帮助你把一个模糊的问题拆成清晰的选择。

## 安装到 Codex

```bash
git clone https://github.com/qinxujunai/sun.git
mkdir -p ~/.codex/skills
if [ -e ~/.codex/skills/sun ]; then
  echo "sun 已存在，请先备份并手动合并。"
else
  cp -R sun/skills/sun ~/.codex/skills/sun
fi
```

如果目标目录已存在，先备份并合并，避免覆盖自己的资料。新对话中输入 `$sun`，例如：

> `$sun 帮我分析：我应该保留工作试创业，还是辞职全职投入？`

公开包包含认知模型与《高性价比人生指南》。播客逐字稿不包含在公开包中；没有导入时，技能会说明缺少原文，不会假装可以引用。

## 导入自行取得的逐字稿

把下方路径替换为本机存放播客 Markdown 文件的文件夹：

```bash
python3 ~/.codex/skills/sun/scripts/import_transcripts.py '/你的逐字稿文件夹'
```

若目标已存在，导入会停止，不覆盖文件。搜索并查看原文：

```bash
python3 ~/.codex/skills/sun/scripts/search_knowledge.py 创业 风险 --limit 4
```

## 来源与许可

- 认知框架参考 [0xquqi/sun-skill](https://github.com/0xquqi/sun-skill)，其 README 声明 MIT；本项目的模型手册为重新整理的内容。
- 《[高性价比人生指南](https://github.com/eternity4719/HowToLiveBetter)》正文版本 `36c78569a8d21f26c7c650d2993c7103832ca4b5`，遵循 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，保留原文及许可。复制时未改动正文；其中第三方材料和链接的权利需分别确认。
- 播客转写参考 [justin-sun-podcast-markdown](https://github.com/diverHansun/justin-sun-podcast-markdown)，公开包不分发逐字稿。

指南中的等级由原作者评定，地区、日期和适用人群可能影响结论。人物观点是历史材料；技能不是本人，也不能保证预测或决策结果。

## 本地预览网站

用浏览器打开 `docs/index.html`，或在仓库目录运行 `python3 -m http.server 8000 --directory docs`。

项目自有代码按 MIT 许可发布，见 [LICENSE](LICENSE)。第三方资料按各自许可使用，详见上面的来源与许可。

## 暂存交接

[项目对话与决策记录](TEMPORARY_PROJECT_CONTEXT.md)供后续协作参考，项目经确认后可删除。
