from fabric.api import *

import os

env.user = 'root'
env.hosts = ['ali']


def deploy():
    pwd = os.getcwd()
    #sudo("chown {} -R /var/www/album".format(env.user))
    local('rsync -az --exclude-from=rsync_exclude --progress '
          '{}/ ali:/var/www/huatuo/'.format(pwd))
    #sudo("chown www-data -R /var/www/album")
    local('rsync -az --exclude-from=rsync_exclude --progress '
          '{}/ ali:/tmp/huatuo/'.format(pwd))
    with cd('/var/www/huatuo'):
        # now setup the package with our virtual environment's
        # python interpreter
        run('huatuoenv/bin/pip install -r requirements.txt ')
    # and finally touch the .wsgi file so that mod_wsgi triggers
    # a reload of the application
    run('touch /tmp/wsgi.sock')


def bootstrap():
    run('mkdir -p /var/www/huatuo')
    run('chown -R www-data:www-data /var/www/huatuo')
    with cd('/var/www/huatuo'):
        run('virtualenv huatuoenv')
