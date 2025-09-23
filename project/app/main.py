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
  instana_service_name = os.environ.get('INSTANA_SERVICE_NAME', '<strong>null</strong>')
  instana_log_level = os.environ.get('INSTANA_LOG_LEVEL', '<strong>null</strong>')
  py_fast_api_service_host = os.environ.get('PY_FAST_API_SERVICE_HOST', '<strong>null</strong>')
  kubernetes_service_host = os.environ.get('KUBERNETES_SERVICE_HOST', '<strong>null</strong>')
  pod_ip = os.environ.get ('THIS_POD_IP', '<strong>null</strong>')
  instana_eum_reportingUrl = os.environ.get ('INSTANA_EUM_REPORTING_URL', '<strong>null</strong>')
  instana_eum_key = os.environ.get ('INSTANA_EUM_KEY', '<strong>null</strong>')

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
            INSTANA_SERVICE_NAME: """ + instana_service_name + """<br>
            INSTANA_LOG_LEVEL: """ + instana_log_level + """<br>
            PY_FAST_API_SERVICE_HOST: """ + py_fast_api_service_host + """<br>
            KUBERNETES_SERVICE_HOST: """ + kubernetes_service_host + """<br>
            THIS_POD_IP: """ + pod_ip + """
        </div>
    </body>
  </html>
  <script>
    (function(s,t,a,n){s[t]||(s[t]=a,n=s[a]=function(){n.q.push(arguments)},
    n.q=[],n.v=2,n.l=1*new Date)})(window,"InstanaEumObject","ineum");

    ineum('reportingUrl', '""" + instana_eum_reportingUrl + """');
    ineum('key', '""" + instana_eum_key + """');
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
