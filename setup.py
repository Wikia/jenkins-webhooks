from setuptools import setup

from webhooks import __version__

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='webhooks',
    version=__version__,
    description='Flask app for triggering Jenkins builds by GitHub webhooks',
    long_description=long_description,
    url='https://github.com/Wikia/jenkins-webhooks',
    author='macbre',
    author_email='macbre@wikia-inc.com',
    packages=['webhooks'],
    install_requires=[
        'Flask==0.10.1',
        'jenkinsapi==0.3.6',
        'pytest==2.6.0',
        'pyyaml==3.11',
        'mock==1.0.1',
        'gunicorn==19.5.0',
        'gevent==1.0.2',
        'greenlet==0.4.9'
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'webhooks-server=webhooks.app:run'
        ],
    },
)
