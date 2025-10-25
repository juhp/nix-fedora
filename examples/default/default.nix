{ pkgs ? import <nixpkgs> {} }:

# Use the writeTextFile function to create a simple script
pkgs.writeTextFile {
  # Define the package's output name in the Nix store
  name = "hello-script";

  # The path and name of the resulting file in the final package
  destination = "/bin/hello";

  # The content of the file
  text = ''
    #!/bin/sh
    echo "Hello from a reproducible Nix package!"
  '';

  # Make the script executable
  executable = true;
}
# Run with: nix-build
