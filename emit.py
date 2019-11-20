from cuid import cuid
from datetime import datetime, timezone
from kubernetes import client, config

config.load_kube_config()
# config.load_incluster_config()

ui_server_deploy = client.AppsV1Api().\
                   read_namespaced_deployment('ui-server', 'tmc-dearingj')

first_seen = datetime.now(timezone.utc)
involved_obj = client.V1ObjectReference(
    api_version=ui_server_deploy.api_version,
    kind=ui_server_deploy.kind,
    name=ui_server_deploy.metadata.name,
    namespace=ui_server_deploy.metadata.namespace,
    uid=ui_server_deploy.metadata.uid,
    resource_version=ui_server_deploy.metadata.resource_version,
)


event = client.V1Event(
    involved_object=involved_obj,
    first_timestamp=first_seen,
    last_timestamp=first_seen,
    metadata=client.V1ObjectMeta(
        name=f"ui-server.{cuid()}",
        namespace="tmc-dearingj",
    ),
    source=client.V1EventSource(component="ci-approver"),
    type="Normal",
    reason="Approval",
    message="Manually tested and approved",
)

client.CoreV1Api().create_namespaced_event("tmc-dearingj", event)
