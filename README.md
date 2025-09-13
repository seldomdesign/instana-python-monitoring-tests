# Testing IBM Instana's Python FastAPI monitoring capabilities

A glance at IBM Instana's Python FastAPI monitoring capabilities (tracing, logs, metrics), including complete process of creating, containerize, publish to DockerHUB (yes, it's still free as of Setptember 2025) and test Instana's monitoring capabilities of a Pyhton FastAPI demo app in a K8s cluster.

### Context:
Instana is a full-stack observability platform that provides real-time monitoring and performance management for modern applications, including microservices and cloud-native environments.

Instana claims that, among hundreds of [supported technoligies](https://www.ibm.com/docs/en/instana-observability/latest?topic=configuring-monitoring-supported-technologies) includes also Python, and it does so with a zero-configuration tool that automatically collects key metrics and distributed traces from your Python processes [***official reference](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python#usage).

The official Instana documentation covers the speciffic case for FastAPI monitoring, offering a comprehensive comparison chart based on the chosen [Monitoring method](https://www.ibm.com/docs/en/instana-observability/1.0.304?topic=python-fastapi-monitoring#monitoring-methods), presenting two possible scenarios: Instana AutoTrace webhook or installing Instana Python package.
Reached this point is when it becomes clear that the "zero-configuration tool that automatically collects key metricas and distributed traces" is in fact Instana's [Autotrace Webhook](https://www.ibm.com/docs/en/instana-observability/latest?topic=kubernetes-instana-autotrace-webhook), a Kubernetes and OpenShift-compatible admission controller mutating webhook. As this solution is based on a mutating webhook, presents a lot of challanges for the CI/CD pipelines, altering after deployment all resources that will need it's magic, rendering this zero-effort automated solution inadequate for an Enterprise environmetn. 

Therefore, for the reminder of this test we will focus on the alternative scenario: <strong>[Instana Python package](https://www.ibm.com/docs/en/instana-observability/1.0.304?topic=python-fastapi-monitoring#instana-python-package)</strong>

### Requirements:
- Working K8s cluster (any)
- Instana Agent: [Installing the Instana agent on Kubernetes](https://www.ibm.com/docs/en/instana-observability/latest?topic=agents-installing-kubernetes).

### Based on: 
- Python 3.9
- FastAPI [official example](https://fastapi.tiangolo.com/#example).
- Instana Official Documentation: [Monitoring Python](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python)

# Building the FastAPI demo

The FastApi example is based on `fastapi[standard]` dependency. 
After setting up the [virtual environment](https://fastapi.tiangolo.com/virtual-environments/) install the previously mention `fastapi[standard]` dependency.

In this example we will create and use fastapi-test-app folder
```sh
mkdir fastapi-test-app
cd fastapi-test-app
python3 -m venv ./venv
source ./venv/bin/activate
pip install fastapi[standard]
```

Verify with `pip freeze` that the following depndencies are installed: `fastapi`, `starlette`, `pydantic`, `pydantic_core`, `uvicorn`.

Create the `main.py` file and add the following code (as seen on [fastapi](https://fastapi.tiangolo.com/#create-it))
```sh
cat <<EOF | tee main.py
from typing import Union
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
app = FastAPI(docs_url="/docs", redoc_url="/v3/api-docs")

@app.get("/", response_class=HTMLResponse)
async def html_homepage():
    return """
    <html>
        <head>
            <title>FastAPI HTML homepage</title>
        </head>
        <body>
            <h1>Hello World!</h1>
            <p>
                Refer to 
            </p>
        </body>
    </html>
    """

@app.get("/hello/")
def read_hello_world():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
EOF
```

Test the app with `fastapi dev main.py`




