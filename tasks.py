"""
Source: https://gist.github.com/mfekadu/ceaa65dd158bd45dcfadbbda17b83b03
"""
from invoke import task
import os
import webbrowser

try:
    from StringIO import StringIO  ## for Python 2
except ImportError:
    from io import StringIO  ## for Python 3


"""
HELPERS
"""


def go_to_website(URL, verbose=True):
    """
    given a URL, opens the browser
    """
    print("Opening...", URL) if verbose else None
    webbrowser.open(URL)


"""
TASKS
"""


@task(aliases=("list", "lsit", "ist", "-list", "lis", "li", "slit", "slist"))
def _dash_dash_list(c):
    """
    because i forget --list often and fixz my ttypos
    """
    try:  # because pyinvoke issue #704
        c.run("invoke --list", hide="err")
    except Exception as e:
        print("uh oh, https://github.com/pyinvoke/invoke/issues/704")
        print("but here, try this...\n")
        cmd = 'cat tasks.py | grep def | grep "(\c"'  # \c avoid self-reference
        print(f"$ {cmd}\n")
        c.run(cmd)


@task(aliases=("gh", "repo", "remote", "origin"))
def github(c, username="calpoly-csai", repo="api"):
    """
    opens the GitHub website for this project in default browser
    """
    # optionally just hard code this
    # TODO: look into how to read the .git/ folder to redirect based on that.
    SITE = f"https://github.com/{username}/{repo}"
    go_to_website(SITE)


@task(aliases=("gsit", "gst", "sgit", "gis", "gsi", "giat", "gisr", "gsot", "gost"))
def gist(
    c, edit=False, username="mfekadu", gist_hash="ceaa65dd158bd45dcfadbbda17b83b03"
):
    """
    opens the gist.GitHub.com website for this task.py source code
    """
    SITE = f"https://gist.github.com/{username}/{gist_hash}"
    SITE = f"{SITE}/edit" if edit else SITE
    go_to_website(SITE)


@task(aliases=("ghd", "desktop"))
def github_desktop(c):
    """
    opens the GitHub Desktop app <yes i am *that* lazy>. macOS only.
    """
    c.run("open -a 'GitHub Desktop'")


@task(aliases=("invoke", "wtf", "huh", "what", "umm", "uhh", "idk"))
def go_to_invoke_docs(c):
    """
    opens the docs for the PyInvoke project in default browser
    """
    SITE = "https://www.pyinvoke.org"
    go_to_website(SITE)


@task(help={"name": "Name of the person to say hi to."})
def hi(c, name, help=False):
    """
    Say hi to someone.
    """
    print("Hi {}!".format(name))


@task(aliases=("format", "black", "lint"))
def black_auto_format(c, verbose=True):
    """
    Make the code look nice.
    """
    print("Formatting!")
    cwd = os.getcwd()

    # move up to the directory that contains ".git"
    # which often is the root of a repository
    print("current directory: ", cwd)
    while cwd != "/" and ".git" not in os.listdir(cwd):
        if ".git" not in os.listdir(cwd):
            os.chdir("..")
            cwd = os.getcwd()
            print("current directory: ", cwd)
        else:
            break

    cmd = "black ."
    print("running command: {}".format(cmd))
    c.run("black .")


@task(aliases=("sc", "scala", "hi-scala", "hiscala", "helloscala"))
def hello_scala(c, verbose=True, name="hello_scala"):
    """
    create a hello_world scala file
    """
    filename = f"{name}.sc"
    print(f"Creating {filename}")
    file_content = """import scala.io._
object HelloApp {
    def main(args: Array[String]): Unit = {
        val coder = "Python"
        val num = 21
        println(s"Hello Scala from ${coder}!");
        println(s"${num + num} is a cool num");
    }
}
"""
    with open(filename, "w") as f:
        f.write(file_content)

    cmd = f"cat {filename}"
    print(f"$ {cmd}\n")
    c.run(cmd)

    cmd = f"scala {filename}"
    print(f"$ {cmd}\n")
    c.run(cmd)


@task(aliases=("copy", "pbcopy"))
def copy_tasks_py_to_clipboard(c):
    """
    """
    cmd = "cat tasks.py | pbcopy"
    print(f"$ {cmd}\n")
    c.run(cmd)


@task(aliases=("ssh",))
def copy_ssh(c):
    """
    """
    # https://askubuntu.com/a/811236
    cmd = "ls -p ~/.ssh/ | grep -v /"
    print(f"$ {cmd}\n")
    c.run(cmd)

    choice = input("\n\nWhich one? (enter the name): ")
    print("\n\n")

    cmd = f"cat ~/.ssh/{choice} | pbcopy"
    print(f"$ {cmd}\n")
    c.run(cmd)


@task
def docker(c, username=None, app_name="nimbus"):
    """
    Locally, docker build && docker run
    """
    ENV_KEY = "TASKS_DOCKER_USERNAME"
    if username is not None:
        print("hey run this to make life easier...")
        print(f"export {ENV_KEY}={username}")
    else:
        try:
            username = os.environ[ENV_KEY]
        except Exception as e:
            username = input("docker username? ")
            print("hey run this to make life easier...")
            print(f"export {ENV_KEY}={username}")

    print("make first sure to run...")
    print("source .export_env_vars")
    print("\n\n")

    try:
        DATABASE_HOSTNAME = os.environ["DATABASE_HOSTNAME"]
        DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
        DATABASE_USERNAME = os.environ["DATABASE_USERNAME"]
        DATABASE_NAME = os.environ["DATABASE_NAME"]
        PYDRIVE_CLIENT_ID = os.environ["PYDRIVE_CLIENT_ID"]
        PYDRIVE_CLIENT_SECRET = os.environ["PYDRIVE_CLIENT_SECRET"]
        GOOGLE_DRIVE_CREDENTIALS = os.environ["GOOGLE_DRIVE_CREDENTIALS"]
        GOOGLE_DRIVE_FOLDER_ID = os.environ["GOOGLE_DRIVE_FOLDER_ID"]
        GOOGLE_CLOUD_NLP_CREDENTIALS = os.environ["GOOGLE_CLOUD_NLP_CREDENTIALS"]
        GOOGLE_CLOUD_NLP_MODEL_NAME = os.environ["GOOGLE_CLOUD_NLP_MODEL_NAME"]
    except Exception:
        print("make first sure to run...")
        print("source .export_env_vars")
        print("\n\n")
        exit()

    # automatically pass in local environment variables into the docker thing
    cmd = "docker build"
    cmd += " --build-arg DATABASE_HOSTNAME"
    cmd += " --build-arg DATABASE_PASSWORD"
    cmd += " --build-arg DATABASE_USERNAME"
    cmd += " --build-arg DATABASE_NAME"
    cmd += " --build-arg PYDRIVE_CLIENT_ID"
    cmd += " --build-arg PYDRIVE_CLIENT_SECRET"
    cmd += " --build-arg GOOGLE_DRIVE_CREDENTIALS"
    cmd += " --build-arg GOOGLE_DRIVE_FOLDER_ID"
    cmd += " --build-arg GOOGLE_CLOUD_NLP_CREDENTIALS"
    cmd += " --build-arg GOOGLE_CLOUD_NLP_MODEL_NAME"
    cmd += f' -t "{username}/{app_name}" .'

    print(f"$ {cmd}\n")
    c.run(cmd, pty=True)  # run the docker build

    # http://www.pyinvoke.org/faq.html#running-local-shell-commands-run
    # --rm will make sure to remove the container on exit of shell
    # otherwise docker containers will eat up your storage space
    cmd = f"docker run -it --rm -p 8080:8080  {username}/{app_name}"
    print(f"$ {cmd}\n")
    c.run(cmd, pty=True)  # run the docker run


@task(aliases=("ds", "dash", "dsh"))
def docker_shell(c, image_name=None):
    """
    Run docker within an interactive shell
    https://stackoverflow.com/a/44769468
    """
    ENV_KEY = "TASKS_DOCKER_IMAGE_NAME"
    if image_name is not None:
        print("hey run this to make life easier...")
        print(f"export {ENV_KEY}={image_name}")
    else:
        try:
            image_name = os.environ[ENV_KEY]
        except Exception as e:
            image_name = input("docker image_name? ")
            print("hey run this to make life easier...")
            print(f"export {ENV_KEY}={image_name}")

    # --rm will make sure to remove the container on exit of shell
    # otherwise docker containers will eat up your storage space
    cmd = f"docker run -it --rm {image_name} sh"
    print(f"$ {cmd}\n")
    c.run(cmd, pty=True)  # run the docker interactive shell
