# 第二轮评测材料说明

controlled_pairs_calibration / validation：共30对，按原始来源组隔离。每对针对一个设计维度移除有用特征，包含同文Tie和轻微排版Tie。expected来自工程构造，不是真人偏好金标准；不用于宣称真实热度或社区准确率。

brief_*：素材抽取与来源审核的写作Brief。引用按连续字符检查，但这不等于证明语义推论正确。源文件始终是事实审核的依据。

naturalness_user_review：三篇中文自然度检查。genuine submissions保留本人实际评价；修订D03获得对话回复“会”，仅确定表达方向。助手编辑稿不算自动生成效果。S01技术背景难判断的备注保留。

final_human_public_pairs：V1/V0的中文随机A/B盲评，private_mapping单独保存，不显示在页面。技术理解不足可填Uncertain。翻译数字机械核对不等于完整语义质量证明。未提交真人结果时明确pending。

final_comparisons：外部模型在冻结后对新素材生成稿进行AB/BA比较；不同意见为Uncertain，不计半胜。身份相同的保留原稿Tie明确注明不是模型裁判投票。

产品测试L开头素材、生成和翻译不能混入Final效果样本。
