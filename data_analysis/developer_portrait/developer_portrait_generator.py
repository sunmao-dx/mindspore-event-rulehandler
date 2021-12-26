"""开发者用户画像分析需要增强的issue数据，即增加label_flag, assign_flag, helper_flag字段作为输入。

   1. 如果社区本身没有任何数据积累，请运行issue_data_analyzer进行数据爬取和数据增强
   2. 如果社区本身有issue数据，请遍历issue数据调用event_classifier内的函数进行数据增强
   3. 如果社区本身有增强的issue数据，请直接运行本脚本生成issue开发者用户画像数据

   注：MindSpore社区目前的实践方式为在issue数据爬取的过程中调用event_classifier内的函数进行数据增强，即上述模式3。
   样例输出结果为issue_label_user_profile.csv
"""