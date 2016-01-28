from setuptools import setup

setup(
    name='album',
    version='0.3',
    long_description=__doc__,
    packages=['album'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-Script',
        'Jinja2',
        'MySQL-python',
        'SQLAlchemy',
        'Werkzeug',
    ]
)
