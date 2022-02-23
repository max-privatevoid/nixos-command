import platform


def normalizeNixosFlakeRef(ref, attribute="toplevel"):
    hostname = platform.node()
    anchorCount = ref.count('#')
    
    assert anchorCount == 1 or anchorCount == 0
    
    if ref.endswith('#') or anchorCount == 0:
        return f"{ref.removesuffix('#')}#nixosConfigurations.\"{hostname}\".config.system.build.{attribute}"
    else:
        flake, anchorHostname = ref.split('#')
        return f"{flake}#nixosConfigurations.\"{anchorHostname}\".config.system.build.{attribute}"

    
def getProfilePath(profile_name):
    return "/nix/var/nix/profiles/system" if not profile_name else f"/nix/var/nix/profiles/system-profiles/{profile_name}"
