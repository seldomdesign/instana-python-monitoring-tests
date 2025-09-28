# Testing IBM Instana’s Python FastAPI Monitoring Capabilities

A look at **IBM Instana’s Python FastAPI monitoring features** — tracing, logs, and metrics — including the full process of creating, containerizing and testing Instana’s monitoring of a Python FastAPI demo app in a Kubernetes (K8s) cluster.

## Context
[IBM Instana](https://www.ibm.com/products/instana) is a **full-stack observability platform** that provides real-time monitoring and performance management for modern applications, including microservices and cloud-native environments.

Instana claims to support **[hundreds of technologies](https://www.ibm.com/docs/en/instana-observability/latest?topic=configuring-monitoring-supported-technologies)**, including Python, via a **“zero-configuration” tool** that automatically collects key metrics and distributed traces from Python processes. [See the official reference](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python#usage)

Instana’s documentation also covers **Python FastAPI monitoring**, providing a [comparison chart](https://www.ibm.com/docs/en/instana-observability/1.0.305?topic=python-fastapi-monitoring#monitoring-methods) for two possible approaches:

1. **Instana AutoTrace Webhook**, or
2. Installing the **Instana Python package**.

At this point, it becomes clear that the so-called *“zero-configuration tool”* is actually the **Instana AutoTrace Webhook**, a Kubernetes and OpenShift compatible admission-controller mutating webhook.


## AutoTrace Webhook Overview
The **Instana AutoTrace Webhook** is promoted as a *“zero-effort”* solution that automatically configures Instana tracing for Node.js, .NET Core, Ruby, and Python applications running in Kubernetes or Red Hat OpenShift clusters.

While this sounds appealing at first, **enterprise-level deployments may face challenges**.
According to the [limitations section](https://www.ibm.com/docs/en/instana-observability/1.0.300?topic=kubernetes-instana-autotrace-webhook#limitations), the webhook only applies to **new K8s resources**, requiring deletion and redeployment of existing Pods, ReplicaSets, StatefulSets, Deployments, and DeploymentConfigs for the webhook to work.

This requirement alone may concern DevOps teams that prefer **no post-pipeline mutations**.
Additional drawbacks include:
- **Manual updates** required for existing instrumentation.
- A **complex removal process** (redeploying all higher-order resources previously modified by the webhook).

In short, organizations using CD tools like **Argo CD** will have to **redeploy all applications** for the webhook to take effect. This often leaves apps in an **“unsynced”** state due to AutoTrace’s post-deployment changes—making this *“zero-effort”* solution **ill-suited for enterprise environments**.


## Chosen Approach: Instana Python Package

For the rest of this walkthrough, we will use the **Instana Python package** approach instead of the AutoTrace Webhook.


### Requirements

- Python 3 development environment
- Docker with image-build capabilities
- Working Kubernetes or OpenShift cluster
- Access to a self-hosted or SaaS Instana tenant
    - SaaS trial works, but logging is limited due to trial restrictions
- Instana Agent deployed on the nodes where the app will run

Based on:
- Python 3.12
- FastAPI [official example](https://fastapi.tiangolo.com/#example)
- Instana [Python monitoring documentations](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python)

---

## Building the FastAPI Demo

FastAPI relies on Starlette and Pydantic, but the `fastapi[standard]` dependency includes everything we need.

**1. Create the project folder and virtual environment:**

```sh
mkdir app
cd app
python3 -m venv ./venv
source ./venv/bin/activate
pip install fastapi[standard]
```
**2. Verify the required packages:**
```sh
pip freeze
# Expected packages: fastapi, starlette, pydantic, pydantic_core, uvicorn
```

**3. Create the application file (`main.py`):**
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

This will create a folder structure similiar to:
```
project/
└── app/
    ├── main.py
    └── venv/
        ├── bin/
        ├── include/
        ├── lib/
        ├── lib64 -> lib/
        └── pyvenv.cfg
```

**4. Test it locally:**
```
fastapi dev main.py
```

You should see the development server running at: `http://127.0.0.1:8000`.

Also, the projects will now include compiled bytecode of imported modules inside `__pycache__` folder:
```
project/
└── app/
    ├── __pycache__/
    ├── main.py
    └── venv/
        ├── bin/
        ├── include/
        ├── lib/
        ├── lib64 -> lib/
        └── pyvenv.cfg
```

---
## Containerizing the Application

**1. Create `requirements.txt` and `Dockerfile` inside project's root folder:**

```sh
cat << EOF | tee requirements.txt
fastapi[standard]~=0.116
pydantic~=2.11
EOF
```

```sh
cat << EOF | tee Dockerfile
FROM python:3.12-slim
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
COPY ./app /code/app
CMD ["fastapi", "run", "app/main.py", "--port", "80"]
EOF
```


**2. Build the Docker image:**

```sh
docker build -t python-fastapi-example:3.12-slim .
```

**3. Run the container for testing:**

```sh
docker run -d --name test-container -p 80:80 python-fastapi-example:3.12-slim
```

Visit `http://localhost` to confirm it’s working.


---

## Adding Instana Python Instrumentation

To enable Instana instrumentation, we’ll use the [manual Python package installation](https://www.ibm.com/docs/en/instana-observability/1.0.304?topic=technologies-monitoring-python#manual-installation) method.

**1. Add the Instana package to `requirements.txt`:**
  ```
  instana~=3.8
  ```

**2.** Rebuild the Docker image and test it locally.

**3. Publish the image** to a container registry.
Allready published images are available at this DockerHub repository: [seldomdesign/instana-python-monitoring-tests
](https://hub.docker.com/r/seldomdesign/instana-python-monitoring-tests/tags)

**4. Create a kubernetes deployment** with the required environment variable: 
```AUTOWRAPT_BOOTSTRAP = instana```

A full list of available environment variables can be found in the [IBM Instana Observability - Environment variables](https://www.ibm.com/docs/en/instana-observability/latest?topic=references-environment-variables) documentation.

---

### Deployment example

The following example is a Kubernetes manifest that uses a Docker-Hub image based on this [project/app/main.py](https://github.com/seldomdesign/instana-python-monitoring-tests/blob/main/project/app/main.py) code.

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: instana-python-demo
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-monitoring-demo
  namespace: instana-python-demo
  labels:
    app: fastapi-monitoring-demo
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fastapi-monitoring-demo
  template:
    metadata:
      labels:
        app: fastapi-monitoring-demo
    spec:
      containers:
      - name: fastapi-monitoring-demo
        image: 'seldomdesign/instana-python-monitoring-tests:python-fastapi-example-with-instana-and-eum.3.12-slim'
        imagePullPolicy: Always
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 300Mi
          limits:
            cpu: 500m
            memory: 1Gi
        env:
          - name: THIS_POD_IP
            valueFrom:
              fieldRef:
                fieldPath: status.podIP
          - name: MY_POD_SERVICE_ACCOUNT
            valueFrom:
              fieldRef:
                fieldPath: spec.serviceAccountName
          - name: AUTOWRAPT_BOOTSTRAP
            value: instana
          # - name: INSTANA_AGENT_HOST
          #   value: 'instana-agent.instana-agent.svc.cluster.local'
          # - name: INSTANA_AGENT_PORT
          #   value: '42699'
          # - name: INSTANA_AUTOPROFILE
          #   value: 'true'
          # - name: INSTANA_ALLOW_ROOT_EXIT_SPAN
          #   value: '1'
          # - name: INSTANA_SERVICE_NAME
          #   value: 'fastapi-monitoring-demo'
          # - name: INSTANA_LOG_LEVEL
          #   value: 'debug'

          ## ---
          ## EUM monitoring (JavaScript endpoint) 
          ## Ref: https://www.ibm.com/docs/en/instana-observability/latest?topic=instana-monitoring-websites
          ## https://www.ibm.com/docs/en/instana-observability/latest?topic=planning-preparing-endpoints-keys#endpoints-for-website-and-mobile-app-agents
          ## ---
          # - name: INSTANA_EUM_REPORTING_URL  
          #   value: 'https://eum.instana.io' 
          # - name: INSTANA_EUM_KEY
          #   value: 'my-website-EUM-provided-key'

---
apiVersion: v1
kind: Service
metadata:
  name: fastapi-monitoring-demo
  namespace: instana-python-demo
spec:
  selector:
    app: fastapi-monitoring-demo
  ports:
  - name: fastapi-monitoring-demo
    protocol: TCP
    port: 80
    targetPort: 80
```

### Example Ingress (Nginx):
```yaml
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-fastapi-monitoring-demo
  namespace: instana-python-demo
spec:
  rules:
  - host: fastapi-monitoring-demo.example-domain.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fastapi-monitoring-demo
            port:
              number: 80
  ingressClassName: nginx
```

## Summary

This guide illustrates:
- Setting up a **FastAPI demo app** with Python 3.12
- **Containerizing** it with Docker
- Deploying to **Kubernetes**
- Enabling **Instana Python instrumentation** without relying on the AutoTrace Webhook

This approach offers **greater control** and avoids the **CI/CD disruptions** often caused by Instana AutoTrace Webhook in enterprise environments.
