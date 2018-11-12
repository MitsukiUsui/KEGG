from setuptools import setup,find_packages

setup(
    name="KEGG",
    version="0.1.1",
    description="inhouse KEGG Module Mapper",
    author="MitsukiUsui",
    package_dir={"KEGG":"package"},
    packages=["KEGG"],
    include_package_data=True,
    install_requires=["pandas"]
)

