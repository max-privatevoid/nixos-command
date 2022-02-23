import platform


def normalizeNixosFlakeRef(ref, attribute="config.system.build.toplevel"):
    hostname = platform.node()
    anchorCount = ref.count('#')
    
    assert anchorCount == 1 or anchorCount == 0
    
    if ref.endswith('#') or anchorCount == 0:
        return f"{ref.removesuffix('#')}#nixosConfigurations.\"{hostname}\".{attribute}"
    else:
        flake, anchorHostname = ref.split('#')
        return f"{flake}#nixosConfigurations.\"{anchorHostname}\".{attribute}"

    
def getProfilePath(profile_name):
    return "/nix/var/nix/profiles/system" if not profile_name else f"/nix/var/nix/profiles/system-profiles/{profile_name}"
