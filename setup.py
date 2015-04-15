import os
import re
from elb_update_security_policy import __version__
from setuptools import setup, find_packages

setup(
    name='elb-update-security-policy',
    version=__version__,
    author="Chris Maxwell",
    author_email="chris@wrathofchris.com",
    description="ELB Security Policy Update Tool",
    url = "https://github.com/WrathOfChris/elb-update-security-policy",
    download_url = 'https://github.com/WrathOfChris/elb-update-security-policy/tarball/%s' % __version__,
    license="Apache",
    include_package_data=True,
    packages=find_packages(),
    install_requires=[
        'boto'
    ],
    entry_points={
        "console_scripts": [
            "elb-update-security-policy = elb_update_security_policy.cli:elb_update_security_policy"
        ]
    }
)
