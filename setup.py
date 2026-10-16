from setuptools import find_packages, setup

setup(
    name="ugreen-nas",
    version="1.1.0",
    packages=find_packages(),
    install_requires=[
        "cryptography>=3.4.0",
    ],
    python_requires=">=3.9",
)
