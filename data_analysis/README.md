# 数据分析组件内容：

包括**开发者用户画像**和**基于用户画像的bot活动规则**两部分。

两个子模块为rule handler APP提供分析数据支持，不需要在线部署，可以人工择时运行或定期运行。

具体功能流程可参考 [Event-Rulehandler | ProcessOn](https://www.processon.com/view/link/6189e22f0791290c3687a99c) 数据分析部分内容。

## developer_portrait 

主要功能：根据开源社区基本数据，进行开发者用户画像分析

- issue数据增强模块 `event_classifier.py` (在没有原始issue数据时，运行`issue_data_analyzer.py`可以同时爬取issue数据并完成数据增强)
- 开发者视角issue行为数据聚合  `developer_portrait_generator.py`

输入：开源社区的基本数据，包括issue，pr及其评论等

输出：开发者在**行为频率、行为能力**两方面上的特征。输出数据用于rule-handler APP的Step 1

## bot_reaction

主要功能：根据bot的运行情况，调整bot的活动规则，让bot的活动规则更适合社区环境。**建议在sunmao运行一段时间并收集足够数据后，再进行回应规则更新。**

- sunmao-bot运行数据收集及增强`sunmao_bot_data_collection`（正在开发中）

- bot回应规则模型训练`reaction_rule_model`（正在开发中）

输入：sunmao-bot的运行数据，及社区基本数据

输出：以开发者**行为频率**和**行为能力**作为维度的二维矩阵，表示bot的回应规则。输出数据用于rule-handler APP的Step 2

