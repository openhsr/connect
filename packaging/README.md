
## Fedora
```bash
sudo dnf config-manager --add-repo https://raw.githubusercontent.com/openhsr/connect/master/packaging/fedora/openhsr-pool.repo
sudo dnf install openhsr-connect
```

## Ubuntu

```bash
curl https://pool.openhsr.ch/pool@openhsr.ch.gpg.key | sudo apt-key add -
sudo apt-add-repository https://pool.openhsr.ch/ubuntu/
sudo apt-get update
sudo apt-get install openhsr-connect
```
