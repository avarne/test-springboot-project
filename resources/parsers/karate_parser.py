import argparse
from bs4 import BeautifulSoup
import os
import datetime
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
m_filePath = str(m_filePath).replace("/resources/parsers", "")
m_Dir = m_filePath + os.sep + "karate" + os.sep + "target" + os.sep + "surefire-reports"
files = os.listdir(m_Dir)


def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def xmlparser():
    testcases = []
    time = datetime.datetime.today().strftime('%d-%b-%Y %H:%M:%S')
    for filename in files:
        if filename.lower().endswith(".xml"):
            with open(m_Dir + os.sep + filename, "r") as f:
                content = f.read()
            soup = BeautifulSoup(content, 'xml')
            for row in soup.find_all("testsuite"):
                for tc in row.find_all("testcase"):
                    failure = tc.find('failure')
                    error = tc.find('error')
                    if failure or error:
                        name = tc.get('name')
                        if "[1][1]" in name:
                            name = str(name).replace("[1][1]", "")
                        testcases.append(name)
    failure_info = {
        "Name": build_code + ":KarateFailure",
        "Build ID": build_code,
        "Date Identified": time,
        "Karate Failures": testcases,
        "Bug Origin": "SE"
    }
    # print(testcases)
    return failure_info


def testcount():
    testcount = 0
    errorcount = 0
    failurecount = 0
    count1 = 0
    count2 = 0
    count3 = 0
    for filename in files:
        if filename.lower().endswith(".xml"):
            with open(m_Dir + os.sep + filename, "r") as f:
                content = f.read()
            soup = BeautifulSoup(content, 'xml')
            for row in soup.find_all("testsuite"):
                a = int(row.get('tests'))
                c = a + testcount
                testcount = c
            for row in soup.find_all("testsuite"):
                a = int(row.get('errors'))
                c = a + errorcount
                errorcount = c
            for row in soup.find_all("testsuite"):
                a = int(row.get('failures'))
                c = a + failurecount
                failurecount = c
    count1 = count1 + testcount
    count2 = count2 + errorcount
    count3 = count3 + failurecount
    failed_test_count = count2 + count3
    passed_test_count = count1 - failed_test_count
    # dict = {'tests': count1, 'errors': count2, 'failures': count3, 'pass': passed_test_count}
    # print(dict)
    push_test_results(count1, passed_test_count, failed_test_count)
    if failed_test_count > 0:
        create_work_task(se_url, username, se_auth_token, owner_code, xmlparser())


def create_work_task(swift_deployment, username, auth_token, owner_code, issue_metadata_list):
    create_eform_endpoint = '/rest/v2/api/EFormService/createEformDataInBulk'
    url = swift_deployment + create_eform_endpoint
    header = {'AuthorizationToken': auth_token}
    create_eform_request_body = {
        "data": {
            "FieldsData": [issue_metadata_list],
            "CreatorLoginId": username,
            "OwnerType": "Prj",
            "OwnerCode": owner_code,
            "ItemType": "ABUG"
        }
    }
    # print(create_eform_request_body)
    response = requests.post(url, json=create_eform_request_body, headers=header)
    print(response.json())


def push_test_results(total_tests, passed_tests, failed_tests):
    url = se_url + "/rest/v2/api/EFormService/modifyEFormItemData"
    print(url)
    if failed_tests > 0:
        build_status = "Failed"
        karate_status = "Failed"
    else:
        build_status = "Pass"
        karate_status = "Pass"
    fields_data = {
        "Type Of Integration Test": "Karate",
        "Total Integration Script Count": total_tests,
        "Pass Integration Scripts Count": passed_tests,
        "Failed Integration Scripts Count": failed_tests,
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
    headers = {"AuthorizationToken": str(se_auth_token), "Content-Type": "application/json"}
    resp = requests.put(url=url, json=input_data, headers=headers)
    print(resp.text, str(resp.status_code))


testcount()

