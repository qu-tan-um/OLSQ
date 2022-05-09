import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="olsq",
    version="0.0.4.1",
    license = "BSD",
    author="Daniel Bochen Tan",
    author_email="bctan@cs.ucla.edu",
    description="Optimal Layout Synthesis for Quantum Computing (OLSQ) for mapping and scheduling quantum circuits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tbcdebug/OLSQ",
    project_urls={
        "Bug Tracker": "https://github.com/tbcdebug/OLSQ/issues",
    },
    install_requires=[
        "networkx>=2.5",
        "z3-solver>=4.8.9.0",
    ],
    packages=setuptools.find_packages(),
    package_data={ "olsq": ["devices/*", "benchmarks/*"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
