from setuptools import setup,find_packages

setup(
    name="KEGG",
    version="0.0.2",
    author="MitsukiUsui",
    include_package_data=True,
    packages=find_packages(),
    install_requires=["pandas"]
)

