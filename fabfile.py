from fabric.api import *
from fabric.decorators import *
from fabric.colors import green, red


env.remote_dir = "/data/apps/cogtree"
env.temp_folder = "/tmp"
env.archive_name = "schema.tar"
env.project_name = "mrschemato"
env.hosts = ['hack.cogtree.com']
env.user = 'cogtree'

def _deploy_repo(path):
    sudo('mkdir -m 777 -p %s' % env.remote_dir)
    tmp_archive = "%s/%s" % (env.temp_folder, env.archive_name)

    with lcd(path):
        puts("Archiving repository")
        local('git archive --prefix=%s/ -o %s HEAD' % (env.project_name,env.archive_name))
        local('mv %s /tmp/' % env.archive_name)
        puts("Moving local archive to %s" % env.remote_dir)
        put(tmp_archive, env.remote_dir)
    with cd(env.remote_dir):
        puts("Unpacking archive on server")
        run('tar xvf %s' % env.archive_name)
        run('rm %s' % env.archive_name)
    with cd(path):
        local('rm %s' % tmp_archive)
    return

def _reload_service(service):
    puts("Reloading %s" % service)
    run("sudo supervisorctl restart %s" % service)
    running = run("ps aux | grep -i %s | grep -i python | wc -l" % service)
    if running == "0":
        puts(red("reloading %s failed" % service))
    else:
        puts(green("Success"))

@task
def deploy():
    path = local('git rev-parse --show-toplevel',capture=True)
    puts("Deploying mrSchemato to %s" % env.host)
    _deploy_repo(path)
    _reload_service("celery")
    _reload_service("mrschemato")
    puts(green("Deployment succeeded."))
