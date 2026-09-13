{
  description = "Architecture kit: reproducible validation and development tools";

  # NixOS 26.05 stable channel snapshot, verified on 2026-09-13.
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/21a67dc470149f337cecafbe965d8d252a390518";

  outputs =
    { nixpkgs, ... }:
    let
      forAllSystems =
        f:
        nixpkgs.lib.genAttrs [ "x86_64-linux" "aarch64-linux" ] (
          system:
          f (
            import nixpkgs {
              inherit system;
              config = { };
              overlays = [ ];
            }
          )
        );
      pythonEnv =
        pkgs:
        pkgs.python314.withPackages (ps: [
          ps.jsonschema
          ps.pyyaml
        ]);
    in
    {
      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = [
            (pythonEnv pkgs)
            pkgs.bashInteractive
            pkgs.coreutils
            pkgs.direnv
            pkgs.git
            pkgs.gnugrep
            pkgs.just
            pkgs.nixfmt
            pkgs.ripgrep
            pkgs.ruff
            pkgs.shellcheck
          ];
          PYTHONNOUSERSITE = "1";
          PYTHONDONTWRITEBYTECODE = "1";
          shellHook = "";
        };
      });

      packages = forAllSystems (pkgs: {
        validator = pythonEnv pkgs;
      });

      formatter = forAllSystems (pkgs: pkgs.nixfmt);

      # This smoke check proves imports and requirement pins, not kit acceptance.
      checks = forAllSystems (pkgs: {
        validator-environment =
          pkgs.runCommand "architecture-kit-validator-environment"
            { nativeBuildInputs = [ (pythonEnv pkgs) ]; }
            ''
              python3 -I - <<'PY'
              from importlib.metadata import version
              from pathlib import Path

              import jsonschema
              import referencing
              import yaml

              for line in Path("${./requirements.txt}").read_text().splitlines():
                  line = line.strip()
                  if not line or line.startswith("#"):
                      continue
                  name, expected = line.split("==")
                  actual = version(name)
                  if actual != expected:
                      raise SystemExit(f"{name}: expected {expected}, got {actual}")
              PY
              touch "$out"
            '';
      });
    };
}
