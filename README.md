# Paperwork-tests

Unit and functional tests for Paperwork.


## Reference system

These tests uses a *screenshot* mechanism to make sure things haven't
changed (see [pytestshot](https://github.com/jflesch/pytestshot#readme)).

It means they have to be run on a reference system:
* A Virtual Machine in Virtual Box (should be optional)
* GNU/Linux Debian stable (freshly installed ; no specific config)
* Gnome 3


## Running the tests

```sh
$ sudo apt install python3-nose
$ sudo pip3 install pytestshot
$ nosetests3 -sv
```

## Implementation

Backend's tests are simple classical tests.

Frontend's tests mostly relies on screenshots. See
[pytestshot](https://github.com/jflesch/pytestshot#readme).
