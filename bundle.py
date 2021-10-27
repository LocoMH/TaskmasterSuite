import subprocess
from distutils import dir_util, file_util, archive_util
import click
import os


def remove_file_or_directory(path):
    remove_file(path)
    remove_directory(path)


def remove_file(path):
    try:
        os.remove(path)
    except:
        pass


def remove_directory(path):
    try:
        dir_util.remove_tree(path)
    except:
        pass


def clear_directories_containing(search):
    files = os.listdir(".")
    for file in files:
        if search in file:
            remove_directory(file)


def bundle_windows(version):

    remove_file_or_directory("dist")
    clear_directories_containing("TaskmasterSuite")

    subprocess.run(["pyinstaller", "sources/app/server.spec"])

    file_util.copy_file("assistant.html", "dist")
    file_util.copy_file("screen.html", "dist")
    file_util.copy_file("LICENSE.mit", "dist")
    file_util.copy_file("README.md", "dist")
    dir_util.copy_tree("sources/frontend", "dist/sources/frontend")
    dir_util.copy_tree("sources/db", "dist/sources/db")
    dir_util.copy_tree("data", "dist/data")

    dir_util.copy_tree("dist", "TaskmasterSuite-Windows-" + version)

    archive_util.make_zipfile(
        "TaskmasterSuite-Windows-" + version, "TaskmasterSuite-Windows-" + version)

    remove_file_or_directory("dist")
    clear_directories_containing("TaskmasterSuite-Windows-" + version)


@click.command()
@click.option('--platform', default="win", help="For which platform it shall be distributed. As of now, only win is possible.")
@click.option('--version', prompt="Please enter a version number (e.g. v1.3.2)",
              help="The version number. Example: v1.3.2")
def start(platform, version):
    if platform == "win":
        bundle_windows(version)


if __name__ == "__main__":
    start()
