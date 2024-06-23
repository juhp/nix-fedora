Nix has two installation modes:

# Multi-user mode

This is recommended by upstream and more seamless.

Just install the `nix` package
and run:
```
$ systemctl start nix-daemon`
```

# Single-user mode

Works in containers like toolbox.

Install the `nix-singleuser` package
and then to complete single-user setup
run:
```
$ sudo chown -R $USER /nix/*
```

# Testing

A simple way to check nix is working is to run `nix-shell -p hello`.
This should after a short while of downloading
put you in a nix shell subprocess where you should be able to run `hello`.
