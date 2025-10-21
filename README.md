# How to setup nix on Fedora.

Nix has two different installation modes:

## Multi-user mode

This is recommended by upstream and more seamless.

Just install the `nix` or `nix-daemon` package
(the latter is recommended by the `nix` package) and run:
```
$ sudo systemctl enable --now nix-daemon
```
or
```
$ sudo systemctl start nix-daemon
```

## Single-user mode

This mode works in rootless containers like toolbox.

Run:
```
$ sudo dnf install nix-singleuser
$ sudo chown -R $USER /nix/*
```

Alternatively you can try this hack to have the nix store within your homedir:
```
$ sudo dnf install nix --exclude nix-daemon
$ sudo mkdir /nix
$ sudo ln -s ~/.local/share/nix/root/nix/store /nix/
```
(the symlink is needed for interactive bash - otherwise one gets: eg
`error: executing shell '/nix/store/2j7r5np0vaz4cnqkymp1mqivmjj1x9xl-bash-interactive-5.3p3/bin/bash': No such file or directory`)

# Testing

A simple way to check nix is working is to run e.g. `nix-shell -p hello`.
After a short while of downloading, this should put you in
a nix shell subprocess where you should be able to run `hello`.

Run `nix help` to learn more about the nix CLI or visit <https://nix.dev/>.
