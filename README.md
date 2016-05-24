# open\HSR Connect
Besser als der HSR Mapper ;)

## Requirements

* python3
* `sudo pip3 install -r requirements.txt`

## CLI

```
Usage:
  openhsr-connect sync [--local-changes=(ask|overwrite|keep|addfiles)] [--remote-deleted=(delete|keep)] [repository]
  openhsr-connect vpn (start|status|stop)
  openhsr-connect print (install|remove) [<printer_name>]

  openhsr-connect help (sync|vpn|print)
  openhsr-connect -h | --help
  openhsr-connect --version


Options:
  -h --help             show this screen.
  --version             show version.
  -v --verbose          increase verbosity
  -q --quiet            suppress non-error messages
  --local-changes=<a>   sync behaviour on local file modifications and new remote file [default: <ask>]
                        options for <a> are: ask, overwrite, keep, addfiles
  --remote-deleted=<a>  sync behaviour on remote file removes. Options for <a> are: delete, keep
```


## Useful Links
* [How rsync works](https://rsync.samba.org/how-rsync-works.html)
* [SMB docs...](https://msdn.microsoft.com/en-us/library/ee878573.aspx)
