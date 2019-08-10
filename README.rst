BLE 5 Research - Scripts and notes
==================================

This repository contains some of the scripts and code I used to test BLE 5
new channel selection algorithm (CSA #2) and its underlying PRNG.

* *csa2_dieharder.c*: byte generator for the Dieharder test suite
* *csa2-hopinter-simulate.py*: hop interval guessing method simulation
* *csa2-simulate.py*: PRNG internal counter guessing method simulation
* *dieharder-results.txt*: the results I got when I tested this PRNG with Dieharder
