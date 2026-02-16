{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs =
    { self, nixpkgs }:
    let
      supportedSystems = [
        "x86_64-linux"
        "x86_64-darwin"
        "aarch64-linux"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
    in
    {
      packages = forAllSystems (system: {
        default =
          with pkgs.${system};
          with python313Packages;
          buildPythonApplication {
            pname = "rejection-sama";
            version = "0.1.0";
            src = ./.;
            format = "pyproject";
            propagatedBuildInputs = [
              discordpy
              flit
              pandas
            ];
          };
      });

      devShells = forAllSystems (system: {
        default = pkgs.${system}.mkShellNoCC {
          packages = with pkgs.${system}; [
            (python39.withPackages (
              ps: with ps; [
                black
                self.packages.${system}.default.buildInputs
              ]
            ))
          ];
        };
      });
    };
}
