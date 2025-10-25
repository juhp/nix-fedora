{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    bash
    # Other tools
    #git
  ];

  # Commands to run immediately when entering the shell (optional)
  shellHook = ''
    echo "Welcome to the bash shell!"
    echo "Bash version: $(bash --version)"
  '';
}
# Run with: nix-shell
