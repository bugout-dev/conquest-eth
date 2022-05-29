from setuptools import find_packages, setup

from backend.version import VERSION

long_description = ""
with open("README.md") as ifp:
    long_description = ifp.read()

setup(
    name="backend",
    version=VERSION,
    packages=find_packages(),
    install_requires=[
        "moonstreamdb",
        "psycopg2-binary",
        "pydantic",
        "sqlalchemy",
        "uvicorn",
    ],
    extras_require={
        "dev": ["black", "isort", "mypy", "types-requests", "types-python-dateutil"],
    },
    package_data={"backend": ["py.typed"]},
    zip_safe=False,
    description="Conquest-eth map data provider.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Moonstream.to",
    author_email="engineering@moonstream.to",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Software Development :: Libraries",
    ],
    url="https://github.com/bugout-dev/moonstream",
    entry_points={"console_scripts": ["cem=backend.cli:main"]},
)