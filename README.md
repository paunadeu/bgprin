# bgprin

bgpdumpy Build Requirements

Debian/Ubuntu:
```
apt install autoconf libtool automake ca-certificates gcc make python-setuptools python-dev libbz2-dev zlib1g-dev libffi-dev
```

Mac OS:
```
brew install autoconf libtool automake
```

Required Python packages:
```
pip3 install psutil
pip3 install inquirer
pip3 install bgpdumpy 
```

```
pip3 install exabgp
sudo mkfifo /var/run/exabgp.{in,out}
sudo mkdir /var/run/exabgp
exabgp --fi > /var/run/exabgp/exabgp.env
sudo mkdir /etc/exabgp && chmod 777 /etc/exabgp
```