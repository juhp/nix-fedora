nix has two installation modes:

# Multi-user mode

This recommended by upstream, is more seamless.

Just install the `nix` package
and run `systemctl start nix-daemon`.

# Single-user mode

Works in containers like toolbox

To complete single-user setup, run:
Install the `nix-singleuser` package
and then run `sudo chown -R $USER /nix/*`.

# Testing

A simple test to check it is working is to run `nix-shell -p hello`.
This should after a short while of downloading
put you in a nix shell where you should be able to run `hello`.
