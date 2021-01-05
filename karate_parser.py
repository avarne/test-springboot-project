import argparse
import os
import requests
import json


PARSER = argparse.ArgumentParser()
PARSER.add_argument("-oc", "--OWNER_CODE", default='IBMC000001INTG')
PARSER.add_argument("-bi", "--BUILD_CODE", default="BLD833")
PARSER.add_argument("-u", "--USERNAME", default="admin_IBM")
PARSER.add_argument("-auth", "--AUTH_CODE", default="dfgjktuierjh")
PARSER.add_argument("-url", "--SE_URL", default='https://ibm.digite.com')
PARSER.add_argument("-ity", "--ITEM_TYPE", default='BULD_f')
ARGS = PARSER.parse_args()

username = str(ARGS.USERNAME)
owner_code = str(ARGS.OWNER_CODE)
se_auth_token = str(ARGS.AUTH_CODE)
build_code = str(ARGS.BUILD_CODE)
se_url = str(ARGS.SE_URL)
item_type = str(ARGS.ITEM_TYPE)
m_filePath = os.getcwd()
m_Dir = m_filePath + os.sep + "karate" + os.sep + "target" + os.sep + "surefire-reports"
files = os.listdir(m_Dir)


def parse_karate_report():
    filePath = m_Dir
    with open(filePath + "/results-json.txt", "r", encoding="UTF-8") as f1:
        content1 = f1.read()
    data1 = json.loads(content1)
    test_count = data1["scenarios"]
    passed_count = data1["passed"]
    failure_count = data1["failed"]
    test_dict = {"tests": test_count, "passed": passed_count, "failures": failure_count}
    # print(test_dict)
    return test_dict


def push_data_to_se(data_json, authToken):
    url = se_url + "/rest/v2/api/EFormService/modifyEFormItemData"
    print(url)
    if data_json["failures"] > 0:
        build_status = "Failed"
        karate_status = "Failed"
    else:
        build_status = "Pass"
        karate_status = "Pass"
    fields_data = {
        "Type Of Integration Test": "Karate",
        "Total Integration Script Count": str(data_json["tests"]),
        "Pass Integration Scripts Count": str(data_json["passed"]),
        "Failed Integration Scripts Count": str(data_json["failures"]),
        "Build Status": build_status,
        "Karate": karate_status
        }
    # print(fields_data)
    input_data = {
        "data": {
            "FieldsData": [fields_data],
            "OwnerType": "Prj",
            "CreatorLoginId": username,
            "OwnerCode": owner_code,
            "ItemType": item_type,
            "ItemCode": build_code
        }
    }
    # print(input_data)
    headers = {"AuthorizationToken": str(authToken), "Content-Type": "application/json"}
    resp = requests.put(url=url, json=input_data, headers=headers)
    print(resp.text, str(resp.status_code))


field_json = parse_karate_report()
push_data_to_se(field_json, se_auth_token)

