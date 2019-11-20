from kubernetes import client, config
from flask import Flask, request, abort
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
    })


app = Flask(__name__)  # pylint: disable=invalid-name


def deploymentApproved(namespace, deployment_name):
    config.load_incluster_config()
    events = client.CoreV1Api().list_namespaced_event(namespace)
    if next(
            filter(lambda e: e.involved_object.name == deployment_name
                   and e.involved_object.kind == 'Deployment'
                   and e.reason == 'Approval', events.items),
            False):
        return True
    return False


@app.route('/', methods=['POST'])
def webhook():
    admission = request.get_json()
    if admission is None:
        abort(400)
    admission_request = admission.get('request', {})
    uid = admission_request.get('uid')
    namespace = admission_request.get('namespace')
    owner_references = admission_request.get('object', {})\
        .get('metadata', {}).get('ownerReferences', [])
    deploy_approved = True
    deployment_name = next(
        filter(lambda r: r['kind'] == 'Deployment', owner_references),
        {}).get('name', None)
    app.logger.info(f"Checking deployment: {deployment_name}")
    if deployment_name is not None:
        deploy_approved = deploymentApproved(namespace, deployment_name)

    resp = {
        'apiVersion': 'admission.k8s.io/v1',
        'kind': 'AdmissionReview',
        'response': {
            'uid': uid,
            'allowed': deploy_approved
        },
    }

    if deploy_approved is False:
        app.logger.info("Denying deployment")
        resp['response']['status'] = {'code': 403, 'message':
                                      'Your deployment must be approved'}
    else:
        app.logger.info("Approving deployment")

    return resp


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=5000)
