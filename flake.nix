{
  inputs = {
    nixpkgs.url     = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        
        playwrightFirefoxOnly = pkgs.playwright-driver.browsers.override {
          withFirefox = true;
          withChromium = false;
          withWebkit = false;
        };
        
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          playwright
          requests
          scrapy
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
          ];

          shellHook = ''
            export PLAYWRIGHT_BROWSERS_PATH=${playwrightFirefoxOnly}
            export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
            export PYTHONPATH="$PWD/src:$PYTHONPATH"
          '';
        };
      }
    );
}
