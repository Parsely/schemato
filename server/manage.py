from __future__ import absolute_import
from flask.ext.script import Manager
from flask.ext.celery import  install_commands as install_celery_commands
import os

from schemato_web import create_app

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.sys.path.insert(0,parentdir)

app = create_app()
manager = Manager(app)
install_celery_commands(manager)

if __name__ == "__main__":
    manager.run()
