import json
import pandas as pd
import requests
import os

LABEL_BOT_URL = os.environ.get('LABEL_BOT_URL', 'http://127.0.0.1:8008')

# Step 1: Multi-dimension developer portrait
def label_developer_portrait(user, user_profile):
    """
    Generating user profile of issue/pr label.
    :param user: issue user_login of open source community
    :param user_profile: issue user_profile data of open source community
    :return: [user_activity, user_habit]
    """

    # user_portrait_classifier
    mean_issue_num = user_profile['issue_num'].mean()
    if user in user_profile.index:
        # user_activity
        if user_profile['issue_num'][user] > mean_issue_num:
            user_activity = 'core_contributor'
        elif user_profile['issue_num'][user] == 1:
            user_activity = 'common_contributor'
        else:
            user_activity = 'common_user'
        # user_habit
        if user_profile['labeled_ratio'][user] >= 0.9:
            user_habit = 'excellent'
        elif 0.5 <= user_profile['labeled_ratio'][user] < 0.9:
            user_habit = 'average'
        else:
            user_habit = 'bad'
    else:
        user_activity = 'first_issuer'
        user_habit = 'none'

    return [user_activity, user_habit]


# Step 2: Iterable rule generators with user profile
def info_rule_generator(issue, developer_portrait, bot_conf):
    """
    :param issue: issue of open source community
    :param developer_portrait: developer portrait by one of the developer_portrait methods
    :param bot_conf: configuration of the community bot
    :return: an info rule
    """
    # Parameter reorganization
    issue_user_login = issue['issueUser']['issueUserID']
    execute_time = issue['issueUpdateTime']
    is_user_ent = issue['issueUser']['isEntUser']
    issue_labels = issue['issueLabel']

    user_activity, user_habit = developer_portrait

    community_assignee_list = bot_conf['community_assignee_list']
    #community_assignee_list_test = bot_conf['community_assignee_list_test']
    info_text_template = bot_conf['info_text_template']
    bot_reaction = bot_conf['bot_reaction']

    # Generating rules
    rules = []
    # rulestest = []

    # if user_activity == 'first_issuer' and user_habit == 'none':

    #     infoContent =  info_text_template['infoText']['assign_maintainer']
    #     assigneeStr = ''
    #     for assignee in community_assignee_list_test:
    #         assigneeStr = assigneeStr + '@' + assignee + ' '
    #     infoContent['general_content'] = infoContent['general_content'].replace('{assign_maintainer_placeholder}', assigneeStr)

    #     info_payload = {
    #         'targetUser': community_assignee_list_test,
    #         'infoType': 'issueComment',
    #         'infoContent': infoContent
    #     }
    #     rule = {
    #         'issueID': issue['issueID'],
    #         'ruleType': 'info',
    #         'exeTime': execute_time,
    #         'infoPayload': info_payload
    #     }
    #     rulestest.append(rule)

    if is_user_ent == 0 or label_handler(issue_labels):
        print("222222222222222222")
        infoContent =  info_text_template['infoText']['assign_maintainer']
        assigneeStr = ''
        for assignee in community_assignee_list:
            assigneeStr = assigneeStr + '@' + assignee + ' '
        infoContent['general_content'] = infoContent['general_content'].replace('{assign_maintainer_placeholder}', assigneeStr)
        info_payload = {
            'targetUser': community_assignee_list,
            'infoType': 'issueComment',
            'infoContent': infoContent
        }
        rule = {
            'issueID': issue['issueID'],
            'ruleType': 'info',
            'exeTime': execute_time,
            'infoPayload': info_payload
        }
        rules.append(rule)


    info_rule = json.loads(bot_reaction[user_activity][user_habit])

    info_payload = {
        'targetUser': [issue_user_login],
        'infoType': info_rule['info_type'],
        'infoContent': info_text_template['infoText']['label_without_recommendation']
    }
    rule = {
        'issueID': issue['issueID'],
        'ruleType': 'info',
        'exeTime': execute_time,
        'infoPayload': info_payload
    }
    rules.append(rule)

    return rules


def action_rule_generator(issue, developer_portrait, bot_conf):
    pass


def rule_generator(issue, user_profile, bot_conf):
    # Step 1: Generate the issue owner portrait
    issue_owner_portrait = label_developer_portrait(issue['issueUser']['issueUserID'], user_profile)
    # Step 2: Generate the rules
    info_rules = info_rule_generator(issue, issue_owner_portrait, bot_conf)
    # Step 3: Import rules from label-bot [https://github.com/TECH4DX/label-bot.git]
    label_bot_rules = get_label_bot_rules("Issue Hook", issue)
    # Step 4: Finish the complete rule list
    rule_list = []
    if not isinstance(info_rules, list) or not isinstance(label_bot_rules, list):
        info_rules = list(info_rules)
        label_bot_rules = list(label_bot_rules)
    rule_list = rule_list + info_rules + label_bot_rules
    rules = list(filter(lambda x: rule_list.count(x) == 1, rule_list)) # Currently rule-handler and label-bot generate some same rules when creating an issue, so de-duplicated them here.
    return rules

def label_handler(labels):
    isContainUser = False
    if labels:
        for label in labels:
            if "user/" in label['labelName']:
                isContainUser = True
                break
    return isContainUser

def convert_payload(issue):
    payload = dict()
    payload["action"] = issue["issueAction"]
    payload["enterprise"] = issue["repoInfo"]["ent"] if issue["repoInfo"]["ent"] != "" else None
    payload["iid"] = issue["issueID"]

    payload_issue = dict()
    # payload_issue["assignee"] = issue["issueAssignee"] # Do not use this field, because label-bot will not unmarshal this one.
    payload_issue["body"] = issue["issueContent"]
    payload_issue["created_at"] = issue["issueTime"]

    # payload_issue_labels = [{"name": labels["labelName"]} for labels in issue["issueLabel"]] if len(issue["issueLabel"]) != 0 else []
    payload_issue_labels = [{"name": labels["labelName"]} for labels in issue["issueLabel"]] if issue["issueLabel"] is not None else [] # issue["issueLabel"] should be empty, but the retriever didn't pass it when empty.
    payload_issue["labels"] = payload_issue_labels

    payload_issue["number"] = issue["issueID"]
    payload_issue["title"] = issue["issueTitle"]
    payload_issue["updated_at"] = issue["issueUpdateTime"]

    payload_issue_user = dict()
    payload_issue_user["login"] = issue["issueUser"]["issueUserID"]
    payload_issue_user["name"] = issue["issueUser"]["issueUserName"]
    payload_issue["user"] = payload_issue_user

    payload_repository = dict()
    payload_repository["name"] = issue["repoInfo"]["repo"]
    payload_repository["namespace"] = issue["repoInfo"]["org"]

    payload["issue"] = payload_issue
    payload["repository"] = payload_repository

    return payload

def get_label_bot_rules(event_type, issue):
    # Label-bot needs the format of payload from Gitee, not customized structure ISSUE posted from data-cache
    payload = convert_payload(issue)

    try:
        resp = requests.post(LABEL_BOT_URL, headers= {"event_type": event_type}, json = payload)
        resp.encoding = 'utf-8'
    except:
        print("Requests err when posting to LABEL_BOT_URL [{}]".format(LABEL_BOT_URL))
        return []
    else:
        if resp.status_code == 200:
            hash_map = json.loads(resp.content)
            rules = [content for content in hash_map.values()]
            return rules
        else:
            return []


if __name__ == "__main__":
    issue_str = '{"issueID":"issueIDabc123", ' \
                '"issueAction":"issueAction：Create、Del...",' \
                '"issueUser":"david-he91",' \
                '"issueUserID":"issueUserIDabc123",' \
                '"issueTime":"RFC3399",' \
                '"issueUpdateTime":"2021-10-14T20:26:30+08:00",' \
                '"issueAssignee":"用户ID？",' \
                '"issueLabel":["SIG/XX", "kind/bug"]}'
    test_issue = json.loads(issue_str)

    label_user_profile = pd.read_csv('config/developer_portrait/issue_label_user_profile.csv').set_index('owner_login')
    label_bot_reaction = pd.read_csv('config/bot_reaction/issue_label_rule_generator.csv').set_index('user_habit')
    community_assignee_list = ['lizi', 'mfl']  # Community Maintainer
    with open("config/info_text_template.json", 'r', encoding='UTF-8') as load_f:
        info_text_template = pd.DataFrame(json.load(load_f)).set_index("infoType")

    bot_conf = {
        'community_assignee_list': community_assignee_list,
        'info_text_template': info_text_template,
        'bot_reaction': label_bot_reaction
    }

    rules = rule_generator(test_issue, label_user_profile, bot_conf)
    print(json.dumps(rules))
