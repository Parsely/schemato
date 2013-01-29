from flask import Flask, jsonify, render_template, request
from flask_celery import Celery
import os
import sys
import re
from collections import defaultdict
import json
from schemato import Schemato

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
stc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
os.sys.path.append(parentdir)

def create_app():
    return Flask("schemato", template_folder=tmpl_dir, static_folder=stc_dir)

app = create_app()

try:
    conf_path = '/'.join(os.path.realpath(__file__).split('/')[:-1])
    #with open('%s/schemato_config.py' % conf_path) as f: pass
    app.config.from_pyfile("%s/schemato_config.py" % conf_path)
except IOError as e:
    raise IOError("No configuration file found. Did you remember to rename example.schemato_config.py to schemato_config.py?")
celery = Celery(app)

@celery.task(name="schemato.validate_task")
def validate_task(url):
    sc = Schemato(url)
    try:
        res = sc.validate()
    except Exception, e:
        print e
        res = {'msg': e.message}
    return [r.to_dict() for r in res]


@app.route('/')
def main():
    try:
        return render_template('index.html')
    except Exception, e:
        print "main: Erorr: %s" % e

@app.route('/validate', methods=['GET', 'POST'])
def validate():
    try:
        res = validate_task.apply_async(args=[request.form['link']])
        status_url = "/status/%s" % (res.task_id,)
        return jsonify({
            "url": status_url
        })
    except Exception, e:
        print "validate: error: %s" % e

@app.route('/status/<task_id>', methods=['GET'])
def status(task_id):
    if validate_task.AsyncResult(task_id).ready():
        retval = jsonify({
            "status": "DONE",
            "data": validate_task.AsyncResult(task_id).get()
        })
    else:
        retval = jsonify({
            "status": "WORKING"
        })
    return retval

if __name__ == "__main__":
    print "To start celery, open another terminal in this directory and run"
    print "python manage.py celeryd -l info -E"
    app.run()
