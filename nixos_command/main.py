import os
import platform
import subprocess
import tempfile

import click


def printDebug(text):
    if "NIXOS_COMMAND_DEBUG" in os.environ and os.environ["NIXOS_COMMAND_DEBUG"] == "1":
        print(text)


def normalizeNixosFlakeRef(ref, attribute="toplevel"):
    hostname = platform.node()
    anchorCount = ref.count('#')
    
    assert anchorCount == 1 or anchorCount == 0
    
    if ref.endswith('#') or anchorCount == 0:
        return f"{ref.removesuffix('#')}#nixosConfigurations.\"{hostname}\".config.system.build.{attribute}"
    else:
        flake, anchorHostname = ref.split('#')
        return f"{flake}#nixosConfigurations.\"{anchorHostname}\".config.system.build.{attribute}"


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


def activationCommandSettings(f):
    f = click.argument("nixargs", nargs=-1)(f)
    f = click.argument("installable", default=".#")(f)
    f = click.option("-p","--profile-name", help="Profile in which NixOS will be installed", type=click.Path())(f)
    return f


def activationCommand(profile_name, installable, nixargs, action):
    toplevel = normalizeNixosFlakeRef(installable)
    performSwitchAction(
        toplevel,
        "/nix/var/nix/profiles/system" if not profile_name else f"/nix/var/nix/profiles/system-profiles/{profile_name}",
        nixargs,
        action)
    
def buildCommand(installable, nixargs, attribute="toplevel"):
    toplevel = normalizeNixosFlakeRef(installable, attribute=attribute)
    realiseNixosConfiguration(toplevel, nixargs, result="result")


@run.command(context_settings={"ignore_unknown_options": True}, help="Build the new configuration.")
@click.argument("installable", default=".#")
@click.argument("nixargs", nargs=-1)
def build(installable, nixargs):
    return buildCommand(installable, nixargs)


@run.command(context_settings={"ignore_unknown_options": True}, help="Build a VM for testing.")
@click.option("-b","--bootloader", help="Build a VM with bootloader.", default=False, is_flag=True)
@click.argument("installable", default=".#")
@click.argument("nixargs", nargs=-1)
def build_vm(bootloader, installable, nixargs):
    return buildCommand(installable, nixargs, attribute="vmWithBootLoader" if bootloader else "vm")


@run.command(context_settings={"ignore_unknown_options": True}, help="Build and activate the new configuration for testing. Does not create a boot entry.")
@activationCommandSettings
def test(profile_name, installable, nixargs):
    return activationCommand(profile_name, installable, nixargs, "test")
    

@run.command(context_settings={"ignore_unknown_options": True}, help="Build the new configuration and make it the boot default.")
@activationCommandSettings
def boot(profile_name, installable, nixargs):
    return activationCommand(profile_name, installable, nixargs, "boot")


@run.command(context_settings={"ignore_unknown_options": True}, help="Build and activate the new configuration, and make it the boot default.")
@activationCommandSettings
def switch(profile_name, installable, nixargs):
    return activationCommand(profile_name, installable, nixargs, "switch")


@run.command(context_settings={"ignore_unknown_options": True}, help="Alias for 'switch'")
@activationCommandSettings
def apply(profile_name, installable, nixargs):
    return activationCommand(profile_name, installable, nixargs, "switch")

    
if __name__ == "__main__":
    run()
