# Testing IBM Instana's Python FastAPI monitoring capabilities

A glance at IBM Instana's Python FastAPI monitoring capabilities (tracing, logs, metrics), including complete process of creating, containerize, publish to DockerHUB (yes, it's still free as of Setptember 2025) and test Instana's monitoring capabilities of a Pyhton FastAPI demo app in a K8s cluster.

### Context:
Instana is a full-stack observability platform that provides real-time monitoring and performance management for modern applications, including microservices and cloud-native environments.

Instana claims that, among hundreds of [supported technoligies](https://www.ibm.com/docs/en/instana-observability/latest?topic=configuring-monitoring-supported-technologies) includes also Python, and it does so with a zero-configuration tool that automatically collects key metrics and distributed traces from your Python processes [***official reference](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python#usage).

The official Instana documentation covers the speciffic case for FastAPI monitoring, offering a comprehensive comparison chart based on the chosen [Monitoring method](https://www.ibm.com/docs/en/instana-observability/1.0.304?topic=python-fastapi-monitoring#monitoring-methods), presenting two possible scenarios: Instana AutoTrace webhook or installing Instana Python package.
Reached this point is when it becomes clear that the "zero-configuration tool that automatically collects key metricas and distributed traces" is in fact Instana's [Autotrace Webhook](https://www.ibm.com/docs/en/instana-observability/latest?topic=kubernetes-instana-autotrace-webhook), a Kubernetes and OpenShift-compatible admission controller mutating webhook. As this solution is based on a mutating webhook it presents challanges for the CI/CD pipelines, altering after deployment commits/syncs all resources that will accept and need it's magic.

In other workds... Anyone who uses CD tools, like ArgoCD for example, will continously have their Apps in an unsynced status, due to Autotrace Webhooks magic, rendering this zero-effort automated solution inadequate for an Enterprise environment.

Therefore, for the reminder of this test we will focus on the alternative scenario: <strong>[Instana Python package](https://www.ibm.com/docs/en/instana-observability/1.0.304?topic=python-fastapi-monitoring#instana-python-package)</strong>

### Requirements:
- Working K8s or OS cluster (any)
- Instana Agent deployed on the cluster: [Installing the Instana agent on Kubernetes](https://www.ibm.com/docs/en/instana-observability/latest?topic=agents-installing-kubernetes).

### Based on: 
- Python 3.12
- FastAPI Example [official example](https://fastapi.tiangolo.com/#example).
- Instana Official Documentation: [Monitoring Python](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python)

# Building the FastAPI demo

FastAPI is based on Starlette and PyDantic packages, but in our case, the FastApi example uses the `fastapi[standard]` dependency which will include all required pachkages.
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

Create the `main.py` (as seen on [fastapi](https://fastapi.tiangolo.com/#create-it))
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

Test the app by running `fastapi dev main.py` while in the `venv` environment. The post result should confirm that the Development Server is up an running, and the app is accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

If everything is working we can now proceed and containerize the applicaiton.


# Build Docker image
Back in the project folder create `Dockerfile` and `requirements.txt` files
```
cat << EOF | tee requirements.txt
fastapi[standard]~=0.116
pydantic~=2.11
EOF

cat << EOF | tee Dockerfile
FROM python:3.9
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
EOF
```





# Add Instana Python package
While in the venv install the instana pip package
```
pip install instana
```
Add few enhancements to the original FastAPI example like:
- new HTML homepage using `HTMLResponse` from `fastapi.responses`
- Instana EUM (javascript)
- and environment information obtained using `os` package.

```
cat << EOF | tee main.py
from typing import Union
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI(docs_url="/v3/api-docs", redoc_url="/redoc")

@app.get("/", response_class=HTMLResponse)
async def html_homepage():
  hostname = os.environ.get('HOSTNAME', '<strong>null</strong>')
  python_versoin = os.environ.get('PYTHON_VERSION', '<strong>null</strong>')
  autowrapt_bootstrap = os.environ.get('AUTOWRAPT_BOOTSTRAP', '<strong>null</strong>')
  instana_autoprofile = os.environ.get('INSTANA_AUTOPROFILE', '<strong>null</strong>')
  instana_allow_root_exit_span = os.environ.get('INSTANA_ALLOW_ROOT_EXIT_SPAN', '<strong>null</strong>')
  instana_agent_host = os.environ.get('INSTANA_AGENT_HOST', '<strong>null</strong>')
  instana_agent_port = os.environ.get('INSTANA_AGENT_PORT', '<strong>null</strong>')
  py_fast_api_service_host = os.environ.get('PY_FAST_API_SERVICE_HOST', '<strong>null</strong>')
  kubernetes_service_host = os.environ.get('KUBERNETES_SERVICE_HOST', '<strong>null</strong>')


  return """
  <html>
    <head>
      <title>FastAPI HTML homepage</title>
    </head>
    <body>
        <h2>FastAPI demo!</h1>

        <div style="position: absolute; top: 50; left: 50;">
            <p>
                Visit <a href="/v3/api-docs">/v3/api-docs</a> for automated Swagger documentation
            </p>
            <p>
                Visit <a href="/redoc">/redoc</a> for alternative ReDoc API documentation
            </p>
            <p>
                For 'items' API endpoint test use <strong>/items/&#60;int&#62;?q=&#60;string&#62;</strong>. For example: <a href="/items/99?q='this is 99th item'">/items/99?q='this is 99th item'</a>
            </p>
        </div>

        <div style="position: absolute; bottom: 50; left: 50;">
            -- ENV:<br>
            HOSTNAME: """ + hostname + """<br>
            PYTHON_VERSION: """ + python_versoin + """<br>
            AUTOWRAPT_BOOTSTRAP: """ + autowrapt_bootstrap + """<br>
            INSTANA_AUTOPROFILE: """ + instana_autoprofile + """<br>
            INSTANA_ALLOW_ROOT_EXIT_SPAN: """ + instana_allow_root_exit_span + """<br>
            INSTANA_AGENT_HOST: """ + instana_agent_host + """<br>
            INSTANA_AGENT_PORT: """ + instana_agent_port + """<br>
            PY_FAST_API_SERVICE_HOST: """ + py_fast_api_service_host + """<br>
            KUBERNETES_SERVICE_HOST: """ + kubernetes_service_host + """
        </div>
    </body>
  </html>
<script>
  (function(s,t,a,n){s[t]||(s[t]=a,n=s[a]=function(){n.q.push(arguments)},
  n.q=[],n.v=2,n.l=1*new Date)})(window,"InstanaEumObject","ineum");

  ineum('reportingUrl', 'https://eum-blue-saas.instana.io');
  ineum('key', '3tMFmIR6TSeJhCaG0ujd9w');
  ineum('trackSessions');
</script>
<script defer crossorigin="anonymous" src="https://eum.instana.io/eum.min.js"></script>
  """

@app.get("/hello/")
def read_hello_world():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
EOF
```


Rebuild the docker image and test it's integrity





