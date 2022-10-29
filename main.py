# Open source community event rule handler REST API service
import os
import json
import pandas as pd
from flask import Flask, request
from rule_generator import rule_generator, label_developer_portrait, info_rule_generator


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"


@app.route('/rulehandler', methods=['POST', 'GET'])
def rulehandler():
    issue = {}
    if request.method == 'POST':
        issue = request.get_json()
    else:
        pass

    # Loading data
    label_user_profile = pd.read_csv('config/developer_portrait/issue_label_user_profile.csv').set_index('owner_login')
    label_bot_reaction = pd.read_csv('config/bot_reaction/issue_label_rule_generator.csv').set_index('user_habit')

    # TODO: Change rules for different communities here. Also, you can defined rules in json file.
    issueOrg = issue['repoInfo']['org']
    issueRepo = issue['repoInfo']['repo']

    community_assignee = open("config/community_assignee.json", 'r', encoding = 'utf-8')
    community_assignee = json.load(community_assignee)
    if issueOrg in community_assignee.keys():
        community_assignee_list = community_assignee[issueOrg]
    else:
        community_assignee_list = community_assignee["other"]

    # community_assignee_list_test = ['clement_li']

    with open("config/info_text_template.json", 'r', encoding='UTF-8') as load_f:
        info_text_template = pd.DataFrame(json.load(load_f)).set_index("infoType")

    bot_conf = {
        'community_assignee_list': community_assignee_list,
#       'community_assignee_list_test': community_assignee_list_test,
        'info_text_template': info_text_template,
        'bot_reaction': label_bot_reaction
    }

    rules = rule_generator(issue, label_user_profile, bot_conf)

    return json.dumps(rules, ensure_ascii=False).encode('utf8')


if __name__ == "__main__":
    # Run a localhost RESTful API
    app.run(debug=True, host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))
