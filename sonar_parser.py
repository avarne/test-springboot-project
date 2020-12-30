import json
import requests
import argparse
#from requests.auth import HTTPBasicAuth


PARSER = argparse.ArgumentParser()
PARSER.add_argument("-c", "--PROJ_NAME", default='spring-boot-mvn-courses')
PARSER.add_argument("-l", "--SE_URL", default='https://ibm.digite.com')
PARSER.add_argument("-u", "--SE_USERNAME", default='7')
PARSER.add_argument("-p", "--SE_PWD", default='8')
PARSER.add_argument("-du", "--SE_DEVOPS_USER", default='admin_IBM')
PARSER.add_argument("-t", "--SE_API_TOKEN", default='gfgdfgdtrtrdtd')
PARSER.add_argument("-s", "--SONAR_SERVER_URL", default='https://ibm-sonar.digite.com/')
PARSER.add_argument("-b", "--BUILD_EFORM_ITEMCODE", default='bld18')
PARSER.add_argument("-o", "--SE_OWNERCODE", default='IBMC000001INTG')


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


def call_se_rest_apt(field_json, authToken):
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
             "ItemType": "GCT_f",
             "ItemCode": build_eform_itemcode}
    headers = {"AuthorizationToken": str(authToken), "Content-Type": "application/json"}
    resp = requests.put(url=url, data=json.dumps(input), headers=headers)
    print(resp.text, str(resp.status_code))


field_json = parse_sonar_report(proj_name)
auth_token = se_api_token
if auth_token is None:
    auth_token = generate_se_login_token()
call_se_rest_apt(field_json, auth_token)
