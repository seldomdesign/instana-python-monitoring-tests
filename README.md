# Testing IBM Instana's Python monitoring capabilities

Describing a complete process of creating, containerize, publish to DockerHUB (yes, it's still free as of Setptember 2025) and test Instana's Python monitoring capabilities in a K8s cluster.
Instana is a full-stack observability platform that provides real-time monitoring and performance management for modern applications, including microservices and cloud-native environments. 
Instana claims that, among hundreds of [supported technoligies](https://www.ibm.com/docs/en/instana-observability/latest?topic=configuring-monitoring-supported-technologies) includes Python also. And it does so with zero-configuration tool that automatically collects key metrics and distributed traces from your Python processes. Or, at least is what it claims: [official reference](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python#usage)

###Requirements:
- Working K8s cluster (any)
- Instana Agent: [Installing the Instana agent on Kubernetes](https://www.ibm.com/docs/en/instana-observability/latest?topic=agents-installing-kubernetes)

###Based on: 
- FastAPI [official example](https://fastapi.tiangolo.com/#example).
- Instana Official Documentation: [Monitoring Python](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python)

