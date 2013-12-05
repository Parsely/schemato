from fabric.api import *
from fabric.contrib.project import rsync_project

VIRTUALENV_NAME = "schemato"
APP_NAME = VIRTUALENV_NAME
FLASK_SCRIPT = "server/schemato_web.py"
DATA_PATH = "/data/apps/cogtree"
APP_PATH = "{}/{}".format(DATA_PATH, APP_NAME)
VIRTUALENV_PATH = "/data/virtualenvs"

env.use_ssh_config = True
env.hosts = ["cogtree@ue1a-hack.cogtree.com"]

def virtualenv_run(cmd):
    run("source {}/{}/bin/activate && {}".format(VIRTUALENV_PATH, VIRTUALENV_NAME, cmd))

@task
def setup_virtualenv():
    """Set up virtualenv on remote machine."""
    run("mkdir -p {}".format(VIRTUALENV_PATH))
    with cd(APP_PATH):
        run("virtualenv {}/{}".format(VIRTUALENV_PATH, VIRTUALENV_NAME))
        virtualenv_run("pip install -r requirements.txt")

@task
def run_devserver():
    """Run the dev Flask server on remote machine."""
    with cd(APP_PATH):
        virtualenv_run("python {} runserver --host=0.0.0.0 --port=8001".format(FLASK_SCRIPT))

@task
def deploy():
    """Deploy project remotely."""
    run("mkdir -p {}".format(APP_PATH))
    rsync_project(remote_dir=APP_PATH,
                  local_dir="./",
                  exclude=("*.pyc", ".git"))

def supervisor_run(cmd):
    sudo("supervisorctl {}".format(cmd), shell=False)

@task
def restart():
    """Restart supervisor service."""
    supervisor_run("restart {}".format(APP_NAME))
    run("sleep 1")
    supervisor_run("tail -800 {}".format(APP_NAME))
