from setuptools import setup, find_packages

setup(
    name="vasai",
    version="1.0.0",
    description="vasAI SDK — AI Activity Recording & Governance Platform",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=["pydantic>=2.0"],
)
