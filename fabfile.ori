from fabric.api import *

env.user = 'root'
env.hosts = ['ali']


def pack():
    # create a new source distribution as tarball
    local('python setup.py sdist --formats=gztar', capture=False)


def deploy():
    dist = local('python setup.py --fullname', capture=True).strip()
    put('dist/{}.tar.gz'.format(dist), '/tmp/huatuo.tar.gz')
    run('mkdir -p /tmp/huatuo')
    with cd('/tmp/huatuo'):
        run('tar zxf /tmp/huatuo.tar.gz')
        with cd('/tmp/huatuo/{}'.format(dist)):
            run('/var/www/huatuo/huatuoenv/bin/python setup.py install')
    run('rm -rf /tmp/huatuo /tmp/huatuo.tar.gz')
    run('touch /var/www/huatuo.wsgi')


def bootstrap():
    run('mkdir -p /var/www/huatuo')
    run('chown -R www-data:www-data /var/www/huatuo')
    with cd('/var/www/huatuo'):
        run('virtualenv huatuoenv')
