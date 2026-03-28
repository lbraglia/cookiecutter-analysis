let
  # unstable, somewhere in 2026-03
  nixpkgs = fetchTarball  "https://github.com/NixOS/nixpkgs/archive/46db2e09e1d3f113a13c0d7b81e2f221c63b8ce9.tar.gz";
   pkgs = import nixpkgs { config = {}; overlays = []; };
in

pkgs.mkShell {

  packages = with pkgs; [
    # python
    (python314.withPackages (python-pkgs: with python-pkgs; [
      # non-strictly needed packages are here other in UV
      tkinter invoke python-telegram-bot
    ]))
    # R
    (rWrapper.override
      {packages = with rPackages; [openxlsx knitr devtools]; })
    # LaTeX
    (pkgs.texlive.combine {inherit (pkgs.texlive) scheme-full
      amsfonts amsmath cm-super ;})
    # Other
    quarto
    biber
  ];

  env.LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
    # numpy libs
    pkgs.stdenv.cc.cc.lib
    pkgs.libz
  ];

  shellHook = ''
    # unset PYTHONPATH
    uv sync
    # source .venv/bin/activate
  '';
}
