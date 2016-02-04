THE ENV

'''
virtualenv huatuoenv

. huatuoenv/bin/activate

pip install flask


THE DATABASE

MySQL v5.6+ is required, download and install it from the official mysql website.
http://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/
The install sequence is like:
common->community-client->client->community-server->server

Import all the sql file in the db folder to initialize.
