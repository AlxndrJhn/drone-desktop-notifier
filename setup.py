from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="dronedesktopnotifier",
    packages=["dronedesktopnotifier"],
    version="0.2",
    license="GNU GPLv3",
    description="Get notified on your desktop when your drone.io build finishes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Alexander Jahn",
    author_email="jahn.alexander@gmail.com",
    url="https://github.com/AlxndrJhn/drone-desktop-notifier",
    download_url="https://github.com/AlxndrJhn/drone-desktop-notifier/archive/0.2.tar.gz",
    keywords=["drone.io", "notification", "drone", "notifier"],
    install_requires=["requests", "urllib3", "termcolor", "validators", "click", "plyer"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)
