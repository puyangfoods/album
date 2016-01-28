from fabric.api import (
    local,
    run,
    env,
    cd,
    sudo,
)

import os

env.use_ssh_config = True
env.hosts = ['iron']


def pack():
    # create a new source distribution as tarball
    local('python setup.py sdist --formats=gztar', capture=False)


def deploy():
    pwd = os.getcwd()
    sudo("chown {} -R /var/www/album".format(env.user))
    local('rsync -az --exclude-from=rsync_exclude --progress '
          '{}/ iron:/var/www/album/'.format(pwd))
    sudo("chown www-data -R /var/www/album")
    local('rsync -az --exclude-from=rsync_exclude --progress '
          '{}/ iron:/tmp/album/'.format(pwd))
    with cd('/tmp/album'):
        # now setup the package with our virtual environment's
        # python interpreter
        run('/home/gobattle/.virtualenvs/albumenv/bin/python '
            'setup.py install')
    # now that all is set up, delete the folder again
    run('rm -rf /tmp/album')
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
    run('touch /tmp/wsgi.sock')
