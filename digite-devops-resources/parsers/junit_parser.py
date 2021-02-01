import argparse
from bs4 import BeautifulSoup
import os
import datetime
import requests

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-oc", "--OWNER_CODE", default='IBMC000001INTG')
PARSER.add_argument("-bi", "--BUILD_CODE", default="BD833")
PARSER.add_argument("-u", "--USERNAME", default="azure devops")
PARSER.add_argument("-url", "--SE_URL", default='https://ibm.digite.com/rest/v2/api/')
PARSER.add_argument("-auth", "--AUTH_CODE", default="test")
PARSER.add_argument("-jui", "--JIRA_UST_ID", default="ICP-71")
PARSER.add_argument("-cbef", "--CREATE_BULK_EFORM", default="EFormService/createEformDataInBulk")
PARSER.add_argument("-mef", "--MODIFY_EFORM", default="EFormService/modifyEFormItemData")
ARGS = PARSER.parse_args()

username = str(ARGS.USERNAME)
owner_code = str(ARGS.OWNER_CODE)
auth_token = str(ARGS.AUTH_CODE)
build_code = str(ARGS.BUILD_CODE)
jira_ust_id = str(ARGS.JIRA_UST_ID)
swift_deployment = str(ARGS.SE_URL)
create_eform_endpoint = str(ARGS.CREATE_BULK_EFORM)
modify_eform_endpoint = str(ARGS.MODIFY_EFORM)
m_filePath = os.getcwd()
m_filePath = str(m_filePath).replace("/digite-devops-resources/parsers", "")
m_Dir = m_filePath + os.sep + "target" + os.sep + "surefire-reports"
files = os.listdir(m_Dir)


# def myconverter(o):
#     if isinstance(o, datetime.datetime):
#         return o.__str__()

def xmlparser():
    testcases = []
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
                        testcases.append(name)
    return testcases

def bugitemids():
    bgitemid=[]
    url = swift_deployment + "EFormService/getEFormItemListWithFilter/Prj/50528/ABUG/ibm_duplicate_junit_bugs/22-Dec-2020 00:00:00"
    header = {'AuthorizationToken': auth_token}
    response = requests.get(url, headers=header)
    #print(response)
    try:
        print(response.json())
        bg_data=response.json()
        json_data=bg_data.get("data").get("Items").get("Item")
        print(json_data)
        for item in json_data:
            a=item['ID']
            bgitemid.append(a)
        print(bgitemid)
        str1 = ","
        stritem=(str1.join(bgitemid))
    except:
        print("there are no open bugitemids")
        stritem=""
        print(stritem)    
    return stritem

def bugitems():
    bugsitems=[]
    bug_item_ids=bugitemids()
    print(bug_item_ids)
    if bug_item_ids == "":
        print("empty bugitems")
    else:
        url = swift_deployment + "EFormService/getEFormItemDetails/ABUG/"+bug_item_ids+"/Junit Failures"
        header = {'AuthorizationToken': auth_token}
        response = requests.get(url, headers=header)
        print(response)
        bugsitems_data=response.json()
            json_data = bugsitems_data.get("data").get("Items").get("Item")
            for item in json_data:
                a=item.get("LabelInfo").get("Value")
                bugsitems.append(a)
            print(bugsitems)
    return bugsitems

def diff_bugs_testcases():
    tli1=xmlparser()
    print("This is tli1"+str(tli1))
    tli2=bugitems()
    print("This is tli2" + str(tli2))
    final_list=[]
    for t1 in tli1:
        if t1 not in tli2:
            final_list.append(t1)
    print("finaldif lisr is"+str(final_list))
    return final_list

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
    push_test_results(count1, passed_test_count, failed_test_count)
    if failed_test_count > 0:
        create_work_task(swift_deployment, username, auth_token, owner_code, diff_bugs_testcases())


def create_work_task(swift_deployment, username, auth_token, owner_code, testcases):
    #create_eform_endpoint = 'EFormService/createEformDataInBulk'
    time = datetime.date.today().strftime('%d-%b-%Y %H:%M:%S')
    for tcs in testcases:
        failure_info = {
            "Name": jira_ust_id + ":" + build_code + ":" +str(tcs),
            "Build ID": build_code,
            "Date Identified": time,
            "Junit Failures": str(tcs),
            "JIRA UST ID": jira_ust_id,
            "Type of Bug": "JUnit",
            "Bug Origin": "SE"
        }
        url = swift_deployment + create_eform_endpoint
        header = {'AuthorizationToken': auth_token}
        create_eform_request_body = {
            "data": {
                "FieldsData": [failure_info],
                "CreatorLoginId": username,
                "OwnerType": "Prj",
                "OwnerCode": owner_code,
                "ItemType": "ABUG"
            }
        }
        response = requests.post(url, json=create_eform_request_body, headers=header)
        print(response.json())


def push_test_results(total_tests, passed_tests, failed_tests):
    #modify_eform_endpoint = '/rest/v2/api/EFormService/modifyEFormItemData'
    url = swift_deployment + modify_eform_endpoint
    header = {'AuthorizationToken': auth_token}
    if failed_tests>0:
        BuildStatus="Failed"
        JunitJaCoCo="Failed"
        JunitFailures=xmlparser()#["Junit Failures"]
    else:
        BuildStatus="Pass"
        JunitJaCoCo="Pass"
        JunitFailures = ""
    Data={"Type Of Unit Test":"JUnit",
          "Total Unit Script Count":total_tests,
          "Pass Unit Scripts Count":passed_tests,
          "Failed Unit Scripts Count":failed_tests,
          "Build Status":BuildStatus,
          "JUnit":JunitJaCoCo,
          "Junit Failures":str(JunitFailures)}
    print(Data)
    modify_eform_req_body = {
        "data":{
        "FieldsData":[Data],
        "OwnerType":"Prj",
        "OwnerCode":owner_code,
        "ItemType":"BULD_f",
        "ItemCode":build_code,
        "CreatorLoginId": username
    }
    }
    response = requests.put(url, json=modify_eform_req_body, headers=header)
    print(response)

testcount()