import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="olsq",
    version="0.1.dev8",
    author="Daniel Bochen Tan",
    author_email="bctan@cs.ucla.edu",
    description="Optimal Layout Synthesis for Quantum Computing (OLSQ) for mapping and scheduling quantum circuits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tbcdebug/OLSQ",
    install_requires=[
        "networkx>=2.5",
        "z3-solver>=4.8.9.0",
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)