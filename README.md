# rblchecker

Use rblchecker to check whether your outgoing mail IP addresses are listed on RBLs.

The following checkers are supported:

* DNS (for hosts in config)
* Microsoft SNDS

# Install

## Generic

Run the following command to create a source distribution:

    python3 setup.py sdist

## PyPI

Run the following command to install the package from PyPI:

    pip3 install rblchecker

# Configure

Find an example config in `config.yml`.

# Usage

Syntax:

    rblchecker --config-path=...

This command runs all checkers.

# Tests

Run tests with pytest:

    pytest tests/
