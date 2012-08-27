from fabric.api import *
from fabric.decorators import *
from fabric.colors import green, red


env.remote_dir = "/data/apps/cogtree"
env.temp_folder = "/tmp"
env.archive_name = "schema.tar"
env.project_name = "mrSchemato"
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
        run('rm %s' % tmp_archive)
    with cd(path):
        local('rm %s' % tmp_archive)
    return

@task
def deploy():
    path = local('git rev-parse --show-toplevel',capture=True)
    puts("Deploying mrSchemato to %s" % env.host)
    _deploy_repo(path)
    puts(green("Deployment succeeded."))
