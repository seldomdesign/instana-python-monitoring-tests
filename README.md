# Testing IBM Instana's Python monitoring capabilities

A glance at IBM Instana's Pyhton monitoring capabilities (tracing, logs, metrics), including complete process of creating, containerize, publish to DockerHUB (yes, it's still free as of Setptember 2025) and test Instana's monitoring capabilities of a Pyhton FastAPI demo app in a K8s cluster.

Instana is a full-stack observability platform that provides real-time monitoring and performance management for modern applications, including microservices and cloud-native environments. 
Instana claims that, among hundreds of [supported technoligies](https://www.ibm.com/docs/en/instana-observability/latest?topic=configuring-monitoring-supported-technologies) includes also Python, and it does so with a zero-configuration tool that automatically collects key metrics and distributed traces from your Python processes [***official reference](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python#usage).


###Requirements:
- Working K8s cluster (any)
- Instana Agent: [Installing the Instana agent on Kubernetes](https://www.ibm.com/docs/en/instana-observability/latest?topic=agents-installing-kubernetes).

###Based on: 
- Python 3.9
- FastAPI [official example](https://fastapi.tiangolo.com/#example).
- Instana Official Documentation: [Monitoring Python](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python)

# Creating the app

