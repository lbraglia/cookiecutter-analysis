{
  description = "Standard development shell flake";

  inputs = {
    # nixos_stable.url = "github:nixos/nixpkgs?ref=nixos-26.05";
    # stable 26.05 as of 2026-06-23
    nixos_stable.url = "github:nixos/nixpkgs?rev=667d5cf1c59585031d743c78b394b0a647537c35";
  };
  
  outputs = { self, nixos_stable }:
    let
      stable = nixos_stable.legacyPackages.x86_64-linux;
    in {
      devShells.x86_64-linux.default = stable.mkShell {
        
        buildInputs = with stable; [
          uv
          (python314.withPackages (python-pkgs: with python-pkgs; [ tkinter ]))
          (rWrapper.override {packages = with rPackages; [openxlsx knitr devtools]; })
          (pkgs.texlive.combine {inherit (pkgs.texlive) scheme-full amsfonts amsmath cm-super ;})
          quarto
          biber
        ];
        
        env.LD_LIBRARY_PATH = stable.pkgs.lib.makeLibraryPath [
          # numpy libs
          stable.pkgs.stdenv.cc.cc.lib
          stable.pkgs.libz
        ];
        
        shellHook = ''
            # unset PYTHONPATH
            uv sync
            # source .venv/bin/activate
            '';       
      };
    };
}
