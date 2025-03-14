from setuptools import setup, find_packages

try:
    from setuptools import setup
except ImportError as err:
    print("To install this package, please install setuptools first.")
    print("You can install it using:")
    print()
    print("pip install setuptools")
    exit()

setup(
    name='w+ basic authentication',
    version='1.0.0',
    description="w+ sample Library for Python3",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.10.0",
        "alibabacloud_tea>=0.3.3, <1.0.0",
        "alibabacloud_tea_openapi>=0.3.6, <1.0.0",
        "alibabacloud_tea_console>=0.0.1, <1.0.0",
        "alibabacloud_tea_util>=0.3.8, <1.0.0"
    ]
)
