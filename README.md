# Testing IBM Instana's Python FastAPI monitoring capabilities

A glance at IBM Instana's Python FastAPI monitoring capabilities (tracing, logs, metrics), including complete process of creating, containerize, publish to DockerHUB and test Instana's monitoring capabilities of a Pyhton FastAPI demo app in a K8s cluster.

### Context:
Instana is a full-stack observability platform that provides real-time monitoring and performance management for modern applications, including microservices and cloud-native environments.

Instana states that, among hundreds of [supported technoligies](https://www.ibm.com/docs/en/instana-observability/latest?topic=configuring-monitoring-supported-technologies) includes also Python, and it does so with a zero-configuration tool that automatically collects key metrics and distributed traces from your Python processes [***official reference](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python#usage).

Furthermore, Instana documentation covers the specific case of Python FastAPI monitoring, offering a comprehensive comparison chart based on the chosen [Monitoring method](https://www.ibm.com/docs/en/instana-observability/1.0.304?topic=python-fastapi-monitoring#monitoring-methods), presenting two possible scenarios: Instana AutoTrace webhook or installing Instana Python package.
Reached this point is when it becomes clear that the "zero-configuration tool that automatically collects key metrics and distributed traces" is in fact Instana's [Autotrace Webhook](https://www.ibm.com/docs/en/instana-observability/latest?topic=kubernetes-instana-autotrace-webhook), a Kubernetes and OpenShift-compatible admission controller mutating webhook. 

Instana AutoTrace webhook is presented as a "zero-effort" solution that will automatically configure Instana tracing on Node.js, .NET Core, Ruby, and Python applications that run in a Kubernetes or Red Hat OpenShift cluster. At first all sounds good, yet, after using it in a Enterprise level environment, it presents challenges for CI/CD pipelines and deployment decisions. 
As confirmed in the [Limitations section] (https://www.ibm.com/docs/en/instana-observability/1.0.300?topic=kubernetes-instana-autotrace-webhook#limitations), it will work only on new K8s resources, requiring deletion of your existing Pods, ReplicaSets, StatefulStes, Deployments, and DeploymentConfigs and redeployment for the Instana AutoTrace webhook to apply its magic.

***
This requirement alone might trigger unwanted reactions from all DevOps Teams that don't like any actors to alter CI/CD pipelines after their completion, yet, this would not be the only thing to take into consideration for a final decision. Details like manual updates required for the already installed instrumentation and the complex removal procedure (requires to redeploy all higher-order resources that were formerly modified by the AutoTrace webhook) will weight heavily against its advantages.

In other words... those who use CD tools (like ArgoCD for example), need to redeploy all Apps for the webhook to be generated and will continuously have their Apps in an unsynced status, due to Instnaa Autotrace webhook after the fact magic, rendering this "zero-effort" automated solution inadequate for an Enterprise environment.
***

Therefore, for the remainder of this test we will focus on the alternative scenario: <strong>[Instana Python package](https://www.ibm.com/docs/en/instana-observability/1.0.304?topic=python-fastapi-monitoring#instana-python-package)</strong>

### Requirements:
- Python3 dev environment
- Docker with package build capabilities
- Working K8s or OS cluster (any)
- Access to a self-hosted or SaaS Instana active Tenant. SaaS trial version will work also with the exception of logging, due to trial version limitations.
- Instana Agent deployed on the nodes the application will be depoyed: [Installing the Instana agent on Kubernetes](https://www.ibm.com/docs/en/instana-observability/latest?topic=agents-installing-kubernetes).

### Based on: 
- Python 3.12
- FastAPI Example [official example](https://fastapi.tiangolo.com/#example).
- Instana Official Documentation: [Monitoring Python](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python)


## Building the FastAPI demo

FastAPI is based on Starlette and PyDantic packages, but, in our case, the FastApi example uses the `fastapi[standard]` dependency which will include all required packages.
After setting up the [virtual environment](https://fastapi.tiangolo.com/virtual-environments/) install the previously mention `fastapi[standard]` dependency.

In this example we will create and use fastapi-test-app as working folder
```sh
mkdir app
cd app
python3 -m venv ./venv
source ./venv/bin/activate
pip install fastapi[standard]
```

Verify with `pip freeze` that the following packages are installed: `fastapi`, `starlette`, `pydantic`, `pydantic_core`, `uvicorn`.

Create the `main.py` and add the example code, as seen on [FastAPI example](https://fastapi.tiangolo.com/#create-it)
```sh
cat << EOF | tee main.py
from typing import Union
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
EOF
```

Test the application by running `fastapi dev main.py` (while in the previously activated `venv` environment). The post result should confirm that the Development Server is up an running, and the application is accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

If everything is working as expected, we can now proceed and containerize the application.


## Docker image
Back in the project folder create `Dockerfile` and `requirements.txt` files as in [FastAPI in Containers - Docker](https://fastapi.tiangolo.com/deployment/docker/) example: [Package Requirement](https://fastapi.tiangolo.com/deployment/docker/#package-requirements), [Dockerfile](https://fastapi.tiangolo.com/deployment/docker/#dockerfile)
```
cat << EOF | tee requirements.txt
fastapi[standard]~=0.116
pydantic~=2.11
EOF

cat << EOF | tee Dockerfile
FROM python:3.12-slim
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
EOF
```

In the same project root folder run the following command to build the docker image locally
```
docker build -t python-fastapi-example:3.12-slim .
```

Run the docker image in a test-container and visit `http://localhost` to verify
```
docker run -d --name test-container -p 80:80 python-fastapi-example:3.12-slim
```

# Add Instana Python package and activate the sensor

In order to enable the instrumentation, we will follow the [Python package manual installation](https://www.ibm.com/docs/en/instana-observability/1.0.304?topic=technologies-monitoring-python#manual-installation) method. This method will require you to add the `instana` python package to the project and use one of two options:
 - without code change: use the environment variable `AUTOWRAPT_BOOTSTRAP=instana` to enable the auto instrumentation at a deployment level.
 - with code change: manually importing the instana package inside the Python application code with `import instana`

Using the first option and, after adding `instana~=3.8` Python package to `requirements.txt`, what's left is to build the docker image and add the `AUTOWRAPT_BOOTSTRAP=instana` environment variable to the deployment manifest.


*** to be continued (soon)



