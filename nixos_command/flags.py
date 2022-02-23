import click


def withInstallable(f):
    f = click.argument("installable", default=".#")(f)
    return f


def withProfile(f):
    f = click.option("-p","--profile-name", help="Profile in which NixOS will be installed")(f)
    return f


def passToNix(f):
    f = click.argument("nixargs", nargs=-1)(f)
    return f


def activationCommand(f):
    f = passToNix(f)
    f = withInstallable(f)
    f = withProfile(f)
    return f