import json
import requests
import argparse
import datetime
import pytz

timeZ_utc = pytz.timezone('Asia/Kolkata')


PARSER = argparse.ArgumentParser()
PARSER.add_argument("-c", "--PROJ_NAME", default='spring-boot-mvn-courses')
PARSER.add_argument("-url", "--SE_URL", default='https://ibm.digite.com/rest/v2/api/')
PARSER.add_argument("-su", "--SE_USERNAME", default='7')
PARSER.add_argument("-p", "--SE_PWD", default='8')
PARSER.add_argument("-u", "--SE_DEVOPS_USER", default='admin_IBM')
PARSER.add_argument("-bity", "--BUILD_ITEM_TYPE", default='BULD_f')
PARSER.add_argument("-t", "--SE_API_TOKEN", default='gfgdfgdtrtrdtd')
PARSER.add_argument("-s", "--SONAR_SERVER_URL", default='https://ibm-sonar.digite.com/')
PARSER.add_argument("-b", "--BUILD_EFORM_ITEMCODE", default='bld18')
PARSER.add_argument("-oc", "--SE_OWNERCODE", default='IBMC000001INTG')
PARSER.add_argument("-jui", "--JIRA_UST_ID", default="ICP-71")
PARSER.add_argument("-cbef", "--CREATE_BULK_EFORM", default="EFormService/createEformDataInBulk")
PARSER.add_argument("-mef", "--MODIFY_EFORM", default="EFormService/modifyEFormItemData")
PARSER.add_argument("-geilwf", "--GET_EFORM_IDS_WITH_FILTER", default="EFormService/getEFormItemListWithFilter")
PARSER.add_argument("-itp", "--ITEM_TYPE", default="Prj")
PARSER.add_argument("-itid", "--ITEM_ID", default="50528")
PARSER.add_argument("-efmtp", "--EFORM_TYPE", default="ABUG")
PARSER.add_argument("-efmfltr", "--EFORM_FILTER", default="ibm_duplicate_junit_bugs")
PARSER.add_argument("-prjdte", "--PROJECT_START_DATE", default="22-Dec-2020 00:00:00")

# PARSER.add_argument("-t", "--SONAR_TOKEN", default='2')
ARGS = PARSER.parse_args()
proj_name = str(ARGS.PROJ_NAME)
se_url = str(ARGS.SE_URL)
se_username = str(ARGS.SE_USERNAME)
se_pass = str(ARGS.SE_PWD)
se_devops_user = str(ARGS.SE_DEVOPS_USER)
se_api_token = str(ARGS.SE_API_TOKEN)
sonar_server_url = str(ARGS.SONAR_SERVER_URL)
build_eform_itemcode = str(ARGS.BUILD_EFORM_ITEMCODE)
item_type = str(ARGS.BUILD_ITEM_TYPE)
se_ownercode = str(ARGS.SE_OWNERCODE)
jira_ust_id =str(ARGS.JIRA_UST_ID)
create_eform_endpoint = str(ARGS.CREATE_BULK_EFORM)
modify_eform_endpoint = str(ARGS.MODIFY_EFORM)
get_eform_ids_with_filter = str(ARGS.GET_EFORM_IDS_WITH_FILTER)
itm_type = str(ARGS.ITEM_TYPE)
itm_id = str(ARGS.ITEM_ID)
efrm_type = str(ARGS.EFORM_TYPE)
efrm_filter = str(ARGS.EFORM_FILTER)
proj_strt_date = str(ARGS.PROJECT_START_DATE)


def generate_se_login_token():
    """
    This fucntion returns the token of Swift ENTP.
    """
    # url = f"{se_url}/rest/api/TokenService/getToken"
    url = se_url + "TokenService/getToken"
    # data = f"Loginid={se_username}&Password={se_pass}"
    data = "Loginid=" + se_username + "&Password=" + se_pass
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post(url=url, data=data, headers=headers)
    token = 0
    if resp.status_code is 200:
        token = json.loads(resp.text).get("data")
    return token


def parse_sonar_report(component):
    """
    This fucntion will parse the sonar result and return the dict of the result
    """
    # auth = HTTPBasicAuth(sonarQube_user, sonarQube_pass)

    genrequest = {
                  "component": component,
                  "metricKeys": "ncloc,complexity,violations,bugs,vulnerabilities,code_smells,violations,coverage"
                  }
    print("url is " + sonar_server_url + "api/measures/component")

    # res = requests.get(f"{solarqube_host}/api/measures/component", params=genrequest, auth=auth)
    res = requests.get(sonar_server_url + "api/measures/component", params=genrequest)

    #print(f"status code {res.status_code}")
    #print(f"status text {res.text}")
    print("status code " + str(res.status_code))
    print("status text " + str(res.text))

    jsondata = json.loads(res.text)
    features = jsondata.get("component").get("measures")
    # result = {"Metric": "Value"}
    result = {}
    for row in features:
        if row.get("value") is not None:
            result[row.get("metric")] = row.get("value")
        else:
            value = row.get("periods")
            result[row.get("metric")] = value[0].get("value")
    print(result)
    return result

    # result_df = pd.DataFrame(list(result.items()))
    # result_df.columns = ["Metric", "Value"]

def bugitemids():
    """
    This function will return a list of open bug eform item id's that are there in Swift ENTP application, these id's list is used to find the testcase names.
    """
    bgitemid=[]
    url = se_url + get_eform_ids_with_filter+"/"+itm_type+"/"+itm_id+"/"+efrm_type+"/"+efrm_filter+"/"+proj_strt_date+" 15:00:00"
    print(url)
    header = {'AuthorizationToken': se_api_token}
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


def call_se_rest_api(field_json, authToken):
    """
    This fucntion will update the result in build eform
    """
    url = se_url + modify_eform_endpoint
    se_field_json = field_json
    se_field_json["Code Smells"] = se_field_json.pop("code_smells", "code_smells")
    se_field_json["Lines Of Code"] = se_field_json.pop("ncloc", "ncloc")
    se_field_json["Code Coverage Percentage"] = se_field_json.pop("coverage", "coverage")
    modify_eform_req_body = {
        "data":{
        "FieldsData":[se_field_json],
        "OwnerType":"Prj",
        "OwnerCode":se_ownercode,
        "ItemType":item_type,
        "ItemCode":build_eform_itemcode,
        "CreatorLoginId": se_devops_user
    }
    }
    headers = {"AuthorizationToken": str(authToken), "Content-Type": "application/json"}
    resp = requests.put(url=url, json=modify_eform_req_body, headers=headers)
    #json.dumps(input)
    print(resp.text, str(resp.status_code))

def create_bug(auth_token):
    """
    This function will create a bug in Swift ENTP when the current run coverage is less than the threshold defined.
    """
    #create_eform_endpoint = '/rest/v2/api/EFormService/createEformDataInBulk'
    url = se_url + create_eform_endpoint
    header = {'AuthorizationToken': auth_token}
    time = datetime.date.today().strftime('%d-%b-%Y %H:%M:%S')
    failure_info = {
        "Name": jira_ust_id + ":" + build_eform_itemcode + ":SonarQubeFailure",
        "Build ID": build_eform_itemcode,
        "Date Identified": time,
        "JIRA UST ID": jira_ust_id,
        "Type of Bug": "SonarQube",
        "Bug Origin": "SE"
    }
    create_eform_request_body = {
        "data": {
            "FieldsData": [failure_info],
            "CreatorLoginId": se_devops_user,
            "OwnerType": "Prj",
            "OwnerCode": se_ownercode,
            "ItemType": "ABUG"
        }
    }
    print(failure_info)
    response = requests.post(url, json=create_eform_request_body, headers=header)
    print(response.json())

def get_sonar_threshold(authToken):
    """
    This function will get the threshold value of codecoverage defined in Swift ENTP
    """
    url = se_url + "EFormService/getEFormItemDetails/STD_f/50501/Complexity,Violations,Vulnerabilities,Code Smells,Bugs,Lines Of Code,Code Coverage Percentage"
    headers = {"AuthorizationToken": str(authToken), "accept": "application/json"}
    resp = requests.get(url=url, headers=headers)
    se_data=resp.json()
    json_data=se_data.get("data").get("Items").get("Item")[0].get("LabelInfo")
    print(json_data)
    return(json_data)

def bug_creation_logic(auth_token):
    """
    This fucntion will verify the threshold value of current run and the value given in Swit ENTP, if the threshold is not met and there is no bug logged in Swift NETP this function will create a new bug.
    """
    se_data=get_sonar_threshold(auth_token)
    sonar_data=parse_sonar_report(proj_name)
    bug_item_ids=bugitemids()
    print(bug_item_ids)
    for i in (0,6):
        if se_data.get("Label")[i]=="Code Coverage Percentage":
            if se_data.get("Value")[i]<sonar_data["coverage"]:
                print("coverage : "+sonar_data["coverage"])
                call_se_rest_api(sonar_data, auth_token)
                print("pass")
            else:
                print("coverage : " + sonar_data["coverage"])
                call_se_rest_api(sonar_data, auth_token)
                if bug_item_ids == "":
                    create_bug(auth_token)
                exit(1)

auth_token = se_api_token
if auth_token is None:
    auth_token = generate_se_login_token()
bug_creation_logic(auth_token)
