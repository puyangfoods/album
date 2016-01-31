from setuptools import setup

setup(
    name='huatuo',
    version='0.1',
    long_description=__doc__,
    packages=['huatuo'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'Flask-Script',
        'Jinja2',
        'pymysql',
        'SQLAlchemy',
        'Werkzeug',
    ]
)
