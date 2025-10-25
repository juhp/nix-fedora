{
  description = "A basic dev shell for a single system.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
  };

  outputs = { self, nixpkgs, builtins }:
    let
      # or hardcode "x86_64-linux"
      system =  builtins.currentSystem;
      pkgs = import nixpkgs { inherit system; };
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [ hello ];
      };
    };
}
# Run with: nix develop
