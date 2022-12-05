import os
import subprocess  # noqa: S404

from flask import Flask, Response, request

app = Flask(__name__)


@app.route('/deploy/')
def deploy():
    key = request.args.get('key', '')
    if not key or key != os.environ['API_KEY']:
        return Response(status=400)

    subprocess.Popen(  # noqa: S603
        ['/bin/bash', '-c', 'docker pull rttest/project-connect-api:prod && sudo service proco-api restart'],
        stdout=open('deploy.log', 'a'),
        stderr=open('deploy.log', 'a'),
    )
    return 'ok'
