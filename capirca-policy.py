import requests
import os
import yaml

requests.packages.urllib3.disable_warnings()
import xmltodict

with open("inventory.yaml", "r") as inventoryFile:
    devices = yaml.safe_load(inventoryFile.read())


nautobotServer = os.getenv("NAUTOBOT_SERVER")
token = os.getenv("NAUTOBOT_TOKEN")
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Token {token}",
}

BASEURL = f"https://{nautobotServer}/api/"


response = requests.get(
    f"{BASEURL}plugins/firewall/capirca-policy", verify=False, headers=headers
).json()

for device in devices:
    firewall = device["hostname"]
    apiKey = device["key"]

    for result in response["results"]:
        if firewall in result["display"]:
            configuration = result["cfg"]
            dictData = xmltodict.parse(configuration, dict_constructor=dict)

            firewallUrl = f"{BASEURL}dcim/devices?name={firewall}"
            firewallData = requests.get(
                firewallUrl, verify=False, headers=headers
            ).json()
            zoneData = firewallData["results"][0]["config_context"]

            dictData["config"]["devices"]["entry"]["vsys"]["entry"]["zone"] = zoneData
            configurationNew = xmltodict.unparse(dictData)

    with open(f"{firewall}-capirca.xml", "w+") as xmlFile:
        xmlFile.write(configurationNew)

    files = {"file": open(f"{firewall}-capirca.xml", "r")}

    pushConfigUrl = (
        f"https://{firewall}/api/?type=import&category=configuration&key={apiKey}"
    )
    pushConfigResponse = requests.post(pushConfigUrl, verify=False, files=files)

    partialLoadUrl = f'https://{firewall}/api/?type=op&cmd=<load><config><partial><from-xpath>/config/devices/entry[@name="localhost.localdomain"]/vsys/entry[@name="vsys1"]</from-xpath><to-xpath>/config/devices/entry[@name="localhost.localdomain"]/vsys/entry[@name="vsys1"]</to-xpath><mode>replace</mode><from>{firewall}-capirca.xml</from></partial></config></load>&key={apiKey}'
    partialLoadResponse = requests.get(partialLoadUrl, verify=False)

    commitUrl = (
        f"https://{firewall}/api/?type=commit&cmd=<commit></commit>&key={apiKey}"
    )
    commitResponse = requests.get(commitUrl, verify=False)
    commitResponseJson = xmltodict.parse(commitResponse.text, dict_constructor=dict)

    deleteConfigUrl = f"https://{firewall}/api/?type=op&cmd=<delete><config><saved>{firewall}-capirca.xml</saved></config></delete>&key={apiKey}"
    deleteConfigResponse = requests.get(deleteConfigUrl, verify=False)
    deleteConfigResponseJson = xmltodict.parse(
        deleteConfigResponse.text, dict_constructor=dict
    )

    os.remove(f"{firewall}-capirca.xml")

    print(f"{firewall} FINISHED!!! \n")
