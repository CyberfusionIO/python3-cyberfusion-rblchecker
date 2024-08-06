"""A setuptools based setup module."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rblchecker",
    version="1.0",
    description="Use rblchecker to check whether your outgoing mail IP addresses are listed on RBLs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    author="William Edwards",
    author_email="support@cyberfusion.nl",
    url="https://github.com/CyberfusionIO/rblchecker",
    platforms=["linux"],
    packages=find_packages(
        include=[
            "rblchecker",
            "rblchecker.*",
        ]
    ),
    data_files=[],
    entry_points={"console_scripts": ["rblchecker=rblchecker.CLI:main"]},
    install_requires=[
        "docopt==0.6.2",
        "schema==0.7.7",
        "requests==2.31.0",
        "netaddr==1.3.0",
        "dnspython==2.6.1",
        "PyYAML==6.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["cyberfusion", "rbl"],
    license="MIT",
)
