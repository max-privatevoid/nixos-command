import os
import platform
import subprocess
import tempfile

import click

from nixos_command import flags, transform


def printDebug(text):
    if "NIXOS_COMMAND_DEBUG" in os.environ and os.environ["NIXOS_COMMAND_DEBUG"] == "1":
        print(text)


def realiseNixosConfiguration(toplevel, nixargs, result, fromFile=False, fromExpr=False):
    nix = [ "nix", "build" ]
    
    # nix handles double-arg errors for us
    if fromFile:
        nix.append("--file")
    
    if fromExpr:
        nix.append("--expr")
    
    nix.extend([ toplevel, "--out-link", result ])
    nix.extend(nixargs)
    printDebug(nix)
    return subprocess.run(nix).returncode == 0


def setNixProfile(profile, result):
    profileDir = os.path.dirname(profile)
    if not os.path.isdir(profileDir):
        try:
            os.mkdir(profileDir)
        except PermissionError as e:
            click.echo(f"While creating profile directory: {e}")
            return False
        
    nix = [ "nix-env", "--profile", profile, "--set", result]
    printDebug(nix)
    return subprocess.run(nix).returncode == 0


def activateNixosConfiguration(result, mode):
    switch = [ os.path.join(result, "bin", "switch-to-configuration"), mode ]
    printDebug(switch)
    return subprocess.run(switch).returncode == 0


def performSwitchAction(toplevel, profile, nixargs, mode):
    with tempfile.TemporaryDirectory() as tmpdir:
        result = os.path.join(tmpdir, "nixos-build")
        if (realiseNixosConfiguration(toplevel, nixargs, result)
            and setNixProfile(profile, result)):
            if not activateNixosConfiguration(result, mode):
                click.echo("warning: errors occured during configuration switch")


@click.group()
def run():
    pass


def activationCommand(profile_name, installable, nixargs, action):
    toplevel = transform.normalizeNixosFlakeRef(installable)
    performSwitchAction(
        toplevel,
        transform.getProfilePath(profile_name),
        nixargs,
        action)
    
def buildCommand(installable, nixargs, attribute="config.system.build.toplevel"):
    toplevel = transform.normalizeNixosFlakeRef(installable, attribute=attribute)
    realiseNixosConfiguration(toplevel, nixargs, result="result")


@run.command(context_settings={"ignore_unknown_options": True}, help="Build the new configuration.")
@flags.withInstallable
@flags.passToNix
def build(installable, nixargs):
    return buildCommand(installable, nixargs)


@run.command(context_settings={"ignore_unknown_options": True}, help="Build a VM for testing.")
@click.option("-b","--bootloader", help="Build a VM with bootloader.", default=False, is_flag=True)
@flags.withInstallable
@flags.passToNix
def build_vm(bootloader, installable, nixargs):
    return buildCommand(installable, nixargs, attribute="vmWithBootLoader" if bootloader else "vm")


@run.command(context_settings={"ignore_unknown_options": True}, help="Build and activate the new configuration for testing. Does not create a boot entry.")
@flags.activationCommand
def test(profile_name, installable, nixargs):
    return activationCommand(profile_name, installable, nixargs, "test")
    

@run.command(context_settings={"ignore_unknown_options": True}, help="Build the new configuration and make it the boot default.")
@flags.activationCommand
def boot(profile_name, installable, nixargs):
    return activationCommand(profile_name, installable, nixargs, "boot")


@run.command(context_settings={"ignore_unknown_options": True}, help="Build and activate the new configuration, and make it the boot default.")
@flags.activationCommand
def switch(profile_name, installable, nixargs):
    return activationCommand(profile_name, installable, nixargs, "switch")


@run.command(context_settings={"ignore_unknown_options": True}, help="Alias for 'switch'")
@flags.activationCommand
def apply(profile_name, installable, nixargs):
    return activationCommand(profile_name, installable, nixargs, "switch")


@run.command(context_settings={"ignore_unknown_options": True}, help="Show the history of the system closure.")
@flags.withProfile
def history(profile_name):
    nix = [ "nix", "profile", "diff-closures",
        "--profile",
        transform.getProfilePath(profile_name)
    ]
    printDebug(nix)
    return subprocess.run(nix).returncode == 0


@run.command(context_settings={"ignore_unknown_options": True}, help="Evaluate an attribute of the configuration.")
@flags.withInstallable
@click.argument("expr", required=False)
def eval(installable, expr):
    # HACK: if expr is not given, try using installable as expr instead
    if not expr:
        # if it's set to the default, assume user is running "nixos eval", in which case we suggest to give an expr
        if installable == ".#":
            raise click.UsageError("Expected an expresssion")
        return eval((".#", installable))

    toplevel = transform.normalizeNixosFlakeRef(installable, attribute=f"config.{expr}")
    nix = [ "nix", "eval", toplevel ]
    printDebug(nix)
    return subprocess.run(nix).returncode == 0


if __name__ == "__main__":
    run()
