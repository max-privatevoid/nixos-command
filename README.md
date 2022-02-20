# nixos-command - a redesign of `nixos-rebuild`

Provides a command `nixos`. This command is meant to bring the NixOS tooling up to par with the Nix3 CLI and especially flakes.

## Supported features

- Verbs
  - [x] `build`
  - [x] `build-vm`
  - [x] `build-vm-with-bootloader` (now `build-vm --bootloader`)
  - [x] `boot`
  - [x] `switch`
  - [x] `apply` (alias for `switch` for that supreme DevOps feel)
  - [x] `test`
  - [ ] `dry-activate`
  - [ ] `dry-build`
  - [ ] `edit`
- Flags
  - [x] `--profile-name`
  - [ ] `--rollback`
  - [ ] `--install-bootloader`
  - [ ] `--build-host`
  - [ ] `--target-host`
- Miscellaneous
  - (?) Building non-flake configurations
  - [ ] `nixos-install`
  - [ ] `nixos-version`
      
## Install

In your user's profile
```
nix profile install github:max-privatevoid/nixos-command
```

Or use it in a temporary shell
```
nix shell github:max-privatevoid/nixos-command
```

## Usage examples

Build the NixOS configuration for the flake in the current directory

```
nixos build
```
Build the NixOS configuration for the host "paris" in `.`

```
nixos build .#paris
```

The classic `nixos-rebuild switch`, assuming /etc/nixos is a flake
```
nixos switch /etc/nixos
```

Build a system from a GitHub repository and activate on next boot
```
nixos boot github:my-company/nixos-infra#styx
```