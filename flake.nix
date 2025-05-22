{
  description = "Bzzz";

  nixConfig.bash-prompt = "Bzzz $ ";

  inputs = {
    nixpkgs-unstable.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs-unstable, flake-utils }:

    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs-unstable { inherit system; overlays = [ ]; };

        # packages - Python 3.11 with the following addon lib - default
        pyLocalDeps = pkgs: (with pkgs; [
          (python311.withPackages(ps: with ps; [
              requests
              beautifulsoup4
              pytest
              matplotlib
              pandas
              requests
            ])
          )
        ]);

        checkDeps = pkgs: (with pkgs; [
          pre-commit
        ]);

        # Dependencies used for simple bash scripts
        shellDeps = pkgs: (with pkgs; [
          bashInteractive
          coreutils
        ]);
      in
      {
        formatter = nixpkgs-unstable.legacyPackages."${system}".nixpkgs-fmt;

        devShells.default = pkgs.mkShell {
          packages = builtins.concatLists [ (pyLocalDeps pkgs) ];
          buildInputs =  checkDeps (pkgs) ++ shellDeps (pkgs);
          shellHook = ''
            pre-commit install
          '';
        };
      }
    );
}
