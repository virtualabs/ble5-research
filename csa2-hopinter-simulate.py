#!/usr/bin/env python3

"""
Bluetooth Low Energy 5 CSA #2 PRNG Research
-------------------------------------------

This script does basically the same as the
one simulating our attack, but it focuses
on the guessing of a connection hopInterval
value.

"""

from random import randint

def pgcd(*n):
    """GCD implementation"""
    def _pgcd(a,b):
        while b: a, b = b, a%b
        return a
    p = _pgcd(n[0], n[1])
    for x in n[2:]:
        p = _pgcd(p, x)
    return p


# Hardcoded Access Address
AA = 0x41fd3e29

def chan_id(access_address):
    """
    Compute channel identifier based on access address
    """
    return ((access_address&0xffff0000)>>16) ^(access_address&0x0000ffff)

def permute(v):
    """
    permute 16 bits values (Vol 6, Part B, 4.5.8.3.2)
    """
    b0 = int(bin((v&0xff00)>>8)[2:].rjust(8,'0')[::-1], 2)
    b1 = int(bin((v&0x00ff))[2:].rjust(8,'0')[::-1], 2)
    return (b0<<8) | b1

def MAM(a, b):
    """
    Multiply, Add, Modulo
    """
    return (17 * a + b) % (2**16)

def unmapped_event_channel_selection(counter, channel_identifier):
    """
    counter is unknown but incremented, channel_identifier is known once you got the AA
    """
    round0 = counter ^channel_identifier
    round1 = MAM(permute(round0), channel_identifier)
    round2 = MAM(permute(round1), channel_identifier)
    round3 = MAM(permute(round2), channel_identifier)
    round4 = round3 ^channel_identifier
    return round4

# Compute channel identifier
chanid = chan_id(AA)

# Generate sequence
seq = []
for i in range(2**16):
    prne = unmapped_event_channel_selection(i, chanid)
    seq.append(prne%37)

counter = randint(0, (2**16)-1)
hop_interval = randint(6, 3200)
candidates = range(65536)
print('[system] Hop interval: %d' % hop_interval)
time_hops = 0

# First, simulate a listen on channel 1 (iterate over counter until 1 is produced)
while seq[counter]!=1:
    counter = (counter + 1)&0xffff
    time_hops += hop_interval

#print('[system] Send packet to channel 1 with counter=%d' % counter)
assert seq[counter]==1
channel = 1
total_hops = 0
base_counter = counter
ref_counter = counter
init_candidates = None

# save previous hops
prev_time_hops = None
# keep tracks of hops
nhops = []
rounds=0

for i in range(10):
    rounds += 1
    # Then, choose the first possible counter value
    counter_candidate = candidates[0]

    # Compute next channel
    total_hops += 1
    next_chan = seq[(counter_candidate+total_hops)%65536]

    # Wait for packet sent on this channel
    prev_counter = counter
    prev_time_hops = time_hops
    counter = (counter+1)&0xffff
    while seq[counter]!=next_chan:
        counter = (counter +1)&0xffff
        time_hops += hop_interval

    # Deduce hops
    total_hops = counter - ref_counter
    hops = counter - prev_counter

    # Deduce hop interval
    nhops.append(time_hops - prev_time_hops)
    prev_time_hops = time_hops

    if len(nhops)>=2:
        print('Deduced hop interval with %d deltas: %d' % (rounds, pgcd(*nhops)))

    channel = next_chan
