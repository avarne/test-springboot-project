import json
import requests
import argparse
import datetime
import pytz

timeZ_utc = pytz.timezone('Asia/Kolkata')


PARSER = argparse.ArgumentParser()
PARSER.add_argument("-c", "--PROJ_NAME", default='spring-boot-mvn-courses')
PARSER.add_argument("-l", "--SE_URL", default='https://ibm.digite.com')
PARSER.add_argument("-u", "--SE_USERNAME", default='7')
PARSER.add_argument("-p", "--SE_PWD", default='8')
PARSER.add_argument("-du", "--SE_DEVOPS_USER", default='admin_IBM')
PARSER.add_argument("-t", "--SE_API_TOKEN", default='gfgdfgdtrtrdtd')
PARSER.add_argument("-s", "--SONAR_SERVER_URL", default='https://ibm-sonar.digite.com/')
PARSER.add_argument("-b", "--BUILD_EFORM_ITEMCODE", default='bld18')
PARSER.add_argument("-oc", "--SE_OWNERCODE", default='IBMC000001INTG')
PARSER.add_argument("-jui", "--JIRA_UST_ID", default="ICP-71")

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
se_ownercode = str(ARGS.SE_OWNERCODE)
jira_ust_id =str(ARGS.JIRA_UST_ID)


def generate_se_login_token():
    # url = f"{se_url}/rest/api/TokenService/getToken"
    url = se_url + "/rest/api/TokenService/getToken"
    # data = f"Loginid={se_username}&Password={se_pass}"
    data = "Loginid=" + se_username + "&Password=" + se_pass
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post(url=url, data=data, headers=headers)
    token = 0
    if resp.status_code is 200:
        token = json.loads(resp.text).get("data")
    return token


def parse_sonar_report(component):
    # auth = HTTPBasicAuth(sonarQube_user, sonarQube_pass)

    genrequest = {
                  "component": component,
                  "metricKeys": "ncloc,complexity,violations,bugs,vulnerabilities,code_smells,violations,coverage"
                  }
    print("url is " + sonar_server_url + "/api/measures/component")

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


def call_se_rest_api(field_json, authToken):
    url = se_url + "/rest/api/EFormService/modifyEFormItemData"
    se_field_json = field_json
    se_field_json["Code Smells"] = se_field_json.pop("code_smells", "code_smells")
    se_field_json["Lines Of Code"] = se_field_json.pop("ncloc", "ncloc")
    se_field_json["Code Coverage Percentage"] = se_field_json.pop("coverage", "coverage")

    print(se_field_json)
    input = {"FieldLabels": ",".join(se_field_json.keys()),
             "FieldValues": ",".join(se_field_json.values()),
             "CreatorLoginId": se_devops_user,
             "OwnerType": "Prj",
             "OwnerCode": se_ownercode,
             "ItemType": "BULD_f",
             "ItemCode": build_eform_itemcode}
    headers = {"AuthorizationToken": str(authToken), "Content-Type": "application/json"}
    resp = requests.put(url=url, data=json.dumps(input), headers=headers)
    print(resp.text, str(resp.status_code))

def create_bug(auth_token):
    create_eform_endpoint = '/rest/v2/api/EFormService/createEformDataInBulk'
    url = se_url + create_eform_endpoint
    header = {'AuthorizationToken': auth_token}
    time = str(datetime.datetime.now(timeZ_utc).strftime('%d-%b-%Y'))+" 00:00:00"
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

    url = se_url + "/rest/v2/api/EFormService/getEFormItemDetails/STD_f/50501/Complexity,Violations,Vulnerabilities,Code Smells,Bugs,Lines Of Code,Code Coverage Percentage"
    headers = {"AuthorizationToken": str(authToken), "accept": "application/json"}
    resp = requests.get(url=url, headers=headers)
    se_data=resp.json()
    json_data=se_data.get("data").get("Items").get("Item")[0].get("LabelInfo")
    print(json_data)
    return(json_data)

def bug_creation_logic(auth_token):

    se_data=get_sonar_threshold(auth_token)
    sonar_data=parse_sonar_report(proj_name)
    for i in (0,6):
        if se_data.get("Label")[i]=="Code Coverage Percentage":
            if se_data.get("Value")[i]<sonar_data["coverage"]:
                print("coverage : "+sonar_data["coverage"])
                call_se_rest_api(sonar_data, auth_token)
                print("pass")
            else:
                print("coverage : " + sonar_data["coverage"])
                call_se_rest_api(sonar_data, auth_token)
                create_bug(auth_token)
                exit(1)

auth_token = se_api_token
if auth_token is None:
    auth_token = generate_se_login_token()
bug_creation_logic(auth_token)
