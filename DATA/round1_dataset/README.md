# 数据说明

主来源：[pszemraj/LocalLLaMA-posts](https://huggingface.co/datasets/pszemraj/LocalLLaMA-posts)，数据卡标注ODC-BY，原归档来自Arctic Shift。保留 `raw/DATASET_CARD.md` 与原始Parquet。所有Reddit作者原始文本仍可能有独立权利；本地课程复现实验不等于取得商业重发布授权。

原始100,679条；免费规则候选20,019；2025月份×规则类型分层随机恢复2,800；审计400；36–38h窗口和二次清洗后2,336。split月份与标签规则见执行协议；不要使用score筛选样本。

- `raw_audit.json/csv`：完整本地数据统计。
- `cleaning_log.csv`：每行去留与理由；非“按热度清洗”。
- `candidate_pool.parquet`：免费规则留下的帖子。
- `recovery_cache/`：完整上游响应与请求时间；可能包含作者等原始公开字段，不放入公开产品日志。
- `recovery_audit.csv` / `recovery_decision.json`：400条恢复与窗口决定证据。
- `recovered_posts.parquet`：score与观察时间来自同一源记录。
- `processed_posts.parquet`：最终模型输入/结果与分区。
- `labels.parquet`：回顾性月份×类型Top25%标签，严格大于阈值；并列不强行打正类。
- `splits/`：时间顺序分区。
- `embeddings/`：真实语义模型输出缓存，仅文本输入，截断4000字符。

初次采集常在发布约17秒后，但少数记录更迟，因此“发布前内容”的归档近似存在局限。作者历史只有本抽样中此前已完成观察的帖子，不等于完整声誉。

研究对象是条件性历史表现，缺曝光、平台推荐、新闻强度与完整作者声誉，不进行因果解释。未经授权不自动发帖，不把原帖当指令。
