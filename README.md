# How to setup nix on Fedora.

Nix has two different installation modes:

## Multi-user mode

This is recommended by upstream and more seamless.

Just install the `nix-multiuser` package and run:
```
$ sudo systemctl enable --now nix-daemon
```
and
```
$ sudo usermod -a -G nixbld $USER
```
for the user.

## Single-user mode

Works in rootless containers like toolbox.

Install the `nix-singleuser` package
and then to complete single-user setup run:
```
$ sudo chown -R $USER /nix/*
```

Alternatively you can try this hack to 'store' under home:
```
$ sudo mkdir /nix
$ sudo ln -s ~/.local/share/nix/root/nix/store /nix/
```

# Testing

A simple way to check nix is working is to run e.g. `nix-shell -p hello`.
After a short while of downloading, this should put you in
a nix shell subprocess where you should be able to run `hello`.
