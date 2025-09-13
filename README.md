# Testing IBM Instana's Python monitoring capabilities

Describing a complete process of creating, containerize, publish to DockerHUB (yes, it's still free as of Setptember 2025) and test Instana's monitoring capabilities of Python FastAPI in a K8s cluster.
Instana is a full-stack observability platform that provides real-time monitoring and performance management for modern applications, including microservices and cloud-native environments

###Requirements:
- Working K8s cluster (any)
- Instana Agent: [Installing the Instana agent on Kubernetes](https://www.ibm.com/docs/en/instana-observability/latest?topic=agents-installing-kubernetes)

###Based on: 
- FastAPI [official example](https://fastapi.tiangolo.com/#example).
- Instana Official Documentation: [Monitoring Python](https://www.ibm.com/docs/en/instana-observability/latest?topic=technologies-monitoring-python)

