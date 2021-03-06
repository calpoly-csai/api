#!/usr/bin/env python3
"""
This script will install/download/compile everything you need to work on Nimbus.
"""

import os
import subprocess
import sys
import argparse
import warnings


# lazily mock the colorful.<color_name> functions until import
def bold_green(s, *args, **kwargs):
    return str(s)


def bold_yellow(s, *args, **kwargs):
    return str(s)


def bold_orange(s, *args, **kwargs):
    return str(s)


def bold_white(s, *args, **kwargs):
    return str(s)


def bold_blue(s, *args, **kwargs):
    return str(s)


def bold_red(s, *args, **kwargs):
    return str(s)


def gray_on_gray(s, *args, **kwargs):
    return str(s)


def reset_color(s, *args, **kwargs):
    return str(s)


def run(
    cmd_tokens,
    fail_msg,
    run_msg=None,
    q=False,
    skip_assert=False,
    warn=False,
    capture_output=False,
    qq=False,
):
    # print(os.path.split(cmd_tokens[0:1])[1] + cmd_tokens[1:])
    fname = os.path.split(cmd_tokens[0])[1]
    args = cmd_tokens[1:]
    run_msg = run_msg or bold_blue(
        "\nrunning... " + " ".join([fname] + args) + "\n", nested=True
    )
    print(run_msg) if not qq else None
    stdout = subprocess.DEVNULL if q else None  # default STDOUT
    stderr = subprocess.DEVNULL if q else None  # default STDERR
    stdout = subprocess.PIPE if capture_output else stdout
    res = subprocess.run(cmd_tokens, stdout=stdout, stderr=stdout)
    if skip_assert:
        return res.stdout.decode("utf-8").strip() if capture_output else res
    else:
        its_good = res.returncode == 0
        if its_good:
            print(bold_blue("✅ it is good.", nested=True)) if not qq else None
            return res.stdout.decode("utf-8").strip() if capture_output else res
        elif warn:
            warnings.warn(
                bold_yellow(reset_color("WARNING: " + fail_msg))
            ) if not q else None
            return res.stdout.decode("utf-8").strip() if capture_output else res
        else:
            assert its_good, bold_red(fail_msg)


if __name__ == "__main__":
    # ==================================================================
    #  GET THE COMMAND LINE ARGUMENTS
    # ==================================================================
    parser = argparse.ArgumentParser(description="Build Nimbus.")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_false",  # default is True so that all the funcs with `q=Q` (True) will be quiet by default  # noqa
        help="optionally be VERBOSE with printouts (default: not verbose).",
    )
    parser.add_argument(
        "--spacy-large",
        action="store_true",
        help="optionally download spacy's `en_core_web_lg` model (default: False).",
    )
    parser.add_argument(
        "--no-overwrite-secrets",
        action="store_true",
        help="optionally avoid passing in --overwrite-all into setup_special_files_from_env (default: False).",
    )
    args = parser.parse_args()
    Q = args.verbose
    SPACY_LARGE = args.spacy_large
    NO_OVERWRITE_SECRETS = args.no_overwrite_secrets

    # =========================================================================
    # GET THE CURRENTLY RUNNING PYTHON EXECUTABLE PATH
    # =========================================================================
    python = sys.executable

    # =========================================================================
    # SOME SCRIPT SETUP
    # =========================================================================
    try:
        # ---------------------------------------------------------------------
        # install some nice-to-have terminal color packages
        # ---------------------------------------------------------------------
        cmd = [
            python,
            "-m",
            "pip",
            "install",
            "colorful",
            "termcolor",
            "ansicolors",
            "colorama",
        ]
        run(cmd, fail_msg="oops color packages failed to install. that's ok.", q=Q)
        from colorama import init
        import colorful as cf
        from colors import strip_color
        from contextlib import contextmanager
        import copy

        # https://github.com/timofurrer/colorful#styles
        cf.use_style("monokai")
        bold_green = cf.bold_green
        bold_orange = cf.bold_orange
        bold_yellow = cf.bold_yellow
        bold_white = cf.bold
        bold_red = cf.bold_magenta
        gray_on_gray = cf.gray_on_gray
        bold_blue = cf.bold_blue

        def reset_color(s, *args, **kwargs):
            if isinstance(s, cf.core.ColorfulString):
                return strip_color(s.orig_string)
            elif isinstance(s, str):
                return strip_color(s)
            else:
                raise NotImplementedError("expected either ColorfulString or str.")

        # shadows mock functions
        init()
        print(bold_green("color!") + bold_orange(" wow!"))
    except Exception as e:
        # ---------------------------------------------------------------------
        # make sure you are not on old python
        # ---------------------------------------------------------------------
        if sys.version_info.major < 3:
            # https://docs.python.org/3/library/exceptions.html#SystemError
            msg = (
                "\n\n"
                + "you are running a python with `sys.version_info.major < 3`"
                + "\n"
                + "\n"
                + str(sys.version)
                + "\n"
                + "\n"
                + "try again with Python >= 3.6.8"
                + "\n"
            )
            raise SystemError(msg)
            exit(1)
        else:
            # otherwise the color packages failed for other reasons. that's ok.
            print(e)
            print("\n\nhmm.. no colors, that's ok.\n\n")

    # =========================================================================
    # INSTALL THE REQUIREMENTS
    # =========================================================================
    cmd = [python, "-m", "pip", "install", "-r", "requirements.txt"]
    run(cmd_tokens=cmd, fail_msg="failed to install requirements", q=Q)

    # =========================================================================
    # SETUP THE SPECIAL/SECRET FILES
    # =========================================================================
    if NO_OVERWRITE_SECRETS:
        cmd = [python, "setup_special_files_from_env.py"]
    else:
        cmd = [python, "setup_special_files_from_env.py", "--overwrite-all"]
    missing_secrets_msg = (
        bold_red(
            "failed to setup special files" + "\n\n" + "you need the ", nested=True
        )
        + bold_orange("nimbus-config-secrets", nested=True)
        + "\n"
        + bold_red(
            "\n"
            + "ask an Nimbus maintainer/admin for help"
            + "\n"
            + "\n"
            + "OR read the "
            + bold_yellow(" setup_special_files_from_env.py ", nested=True)
            + bold_red(
                " file "
                + "and setup the appropriate environment files yourself."
                + "\n\nalso see the "
                + bold_yellow("config_SAMPLE.json", nested=True,),
                nested=True,
            ),
            nested=True,
        )
    )
    res = run(cmd_tokens=cmd, fail_msg=missing_secrets_msg, q=Q, warn=True)
    if res.returncode > 0:
        if "config.json" in os.listdir(os.getcwd()):
            # -----------------------------------------------------------------
            # setup failed, but we can check if `config.json` is already
            # -----------------------------------------------------------------
            print(
                bold_yellow(
                    (
                        "\n\nfound config.json... continuing build...\n\n"
                        "if you do not want your current config.json\n"
                        "please follow the steps in the nimbus-config-secrets reposotiry\n"
                        "ask a Maintainer/Admin for help\n"
                    )
                )
            )
        else:
            # -----------------------------------------------------------------
            # okay, fine. last effort to find `config.json` at root of git dir
            # -----------------------------------------------------------------
            cmd = "git rev-parse --show-toplevel".split(" ")
            top_level_path = run(
                cmd,
                fail_msg="this is not a git directory",
                q=Q,
                warn=True,
                capture_output=True,
                qq=True,
            )
            assert "config.json" in os.listdir(os.getcwd()), missing_secrets_msg

    # =========================================================================
    # INSTALL THE LATEST `urllib3` for reasons
    # =========================================================================
    cmd = [python, "-m", "pip", "install", "--upgrade", "urllib3"]
    res = run(cmd_tokens=cmd, fail_msg="failed to get `urllib3`", q=Q)

    # =========================================================================
    # GET THE `en_core_web_sm` SPACY MODEL
    # =========================================================================
    cmd = [python, "-m", "spacy", "download", "en_core_web_sm"]
    res = run(cmd_tokens=cmd, fail_msg="failed to get `en_core_web_sm`", q=Q)

    # =========================================================================
    # GET THE `en_core_web_lg` SPACY MODEL
    # TODO: consider letting people download the small/medium one...
    # =========================================================================
    if SPACY_LARGE:
        cmd = [python, "-m", "spacy", "download", "en_core_web_lg"]
        res = run(cmd_tokens=cmd, fail_msg="failed to get `en_core_web_lg`", q=Q)
    else:
        print(
            bold_blue(
                "\n\nskipping spacy's `en_core_web_lg` download..."
                "\nnimbus will work with `en_core_web_sm` at least\n"
            )
        )

    # =========================================================================
    # DONE
    # =========================================================================
    print(bold_green("done"))
