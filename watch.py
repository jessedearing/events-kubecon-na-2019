from kubernetes import client, config, watch

config.load_kube_config()
# config.load_incluster_config()

v1 = client.CoreV1Api()
w = watch.Watch()

for event in w.stream(v1.list_namespaced_event, "tmc-dearingj"):
    # This is where you'd do something with an event
    print("EVENT: %s" % event)
