import yaml
import subprocess
import time
import os
import sys
values = {}

Vus = "1"
Rate = "1"
Rps = "100"
Duration = "60s"
Pods = "1"

values["Vus"] = Vus
values["Rate"] = Rate
values["Rps"] = Rps
values["Duration"] = Duration
values["Pods"] = Pods

pythonScript = sys.argv[1]

######___________________________________________Extracting the main python script

script = ""
with open(pythonScript, "r") as locust_script:
    script = "".join(locust_script.readlines())
    values["Script"] = script


######___________________________________________Extracting the IP address

response = (subprocess.check_output(["kubectl", "get", "pods", "-o", "wide"]).decode("utf-8")).split("\n")
for line in response:
    if "dynamic-app" in line:
        pod = line.split()
        values["Ip"] = pod[5]


######___________________________________________Populating the values.yaml file
with open("locust-helm/values.yaml", "w") as value_file:
    value_file.write(yaml.dump(values))



######___________________________________________Deploying Helm
try:
    time.sleep(2)
    if os.system("helm install locust ./locust-helm") != 0:
        print("Error deploying helm.......")
    else:
        print("Helm chart deployed !")
        finished = False
        while True:
            response = (subprocess.check_output(["kubectl", "get", "pods"]).decode("utf-8")).split("\n")
            for line in response:
                if "locust" in line:
                    pod = line.split()
                    print(f"Status: {pod[2]}")
                    if pod[2] == "Completed":
                        results = (subprocess.check_output(["kubectl", "logs", pod[0]]).decode("utf-8"))
                        print(results)
                        finished = True
            if finished :
                break
            time.sleep(30)
finally:
    print("\n\n\n\n........deleting locust instance")
    os.system("helm uninstall locust")