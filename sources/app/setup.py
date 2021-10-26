from setuptools import setup, find_packages


def read_requirements():
    with open("requirements.txt") as req_file:
        content = req_file.read()
        reqs = content.split("\n")

    return reqs


setup(
    name="server",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_requirements(),
    license="MIT",
    entry_points='''
        [console_scripts]
        serve = tm_suite.server:start_server
    '''
)
