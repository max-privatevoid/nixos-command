{
  description = "Application packaged using poetry2nix";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.poetry2nix.url = "github:nix-community/poetry2nix";
  inputs.poetry2nix.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, flake-utils, poetry2nix }:
    {
      # Nixpkgs overlay providing the application
      overlay = nixpkgs.lib.composeManyExtensions [
        poetry2nix.overlay
        (final: prev: {
          # The application
          nixos-command = prev.poetry2nix.mkPoetryApplication {
            projectDir = ./.;
            meta.mainProgram = "nixos";
          };
        })
      ];
    } // (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ self.overlay ];
        };
      in
      {
        packages = {
          nixos-command = pkgs.nixos-command;
        };

        defaultPackage = pkgs.nixos-command;

        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            poetry
            nixos-command.dependencyEnv
          ];
          
          PYTHON = pkgs.nixos-command.dependencyEnv.interpreter;

          inputsFrom = builtins.attrValues self.packages.${system};
          
          shellHook = ''
            alias nixos="python3 -m nixos_command.main"
          '';
        };
      }));
}
