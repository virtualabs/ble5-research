#!/usr/bin/env python3

"""
Bluetooth Low Energy 5 CSA #2 Research
--------------------------------------

This is the script I used to draft my attack
against CSA #2 PRNG.

It simulates a BLE 5 connection between two devices
and an external attacker trying to guess this connection
PRNG counter value.
"""

from random import randint

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

# Replace this value with your access address, or make it random
chanid = chan_id(0xb0a1cd9d)

seq = []
for i in range(2**16):
    prne = unmapped_event_channel_selection(i, chanid)
    seq.append(prne%37)

counter = randint(0, (2**16)-1)
print('[system] Base counter=%d' % counter)

candidates = range(65536)

# First, simulate a listen on channel 1 (iterate over counter until 1 is produced)
while seq[counter]!=1:
    counter = (counter + 1)&0xffff
print('[system] Send packet to channel 1 with counter=%d' % counter)
assert seq[counter]==1
channel = 1
total_hops = 0
base_counter = counter
ref_counter = counter
init_candidates = None

while True:
    # Wait for keyboard press
    input()

    # Then, choose the first possible counter value
    counter_candidate = candidates[0]
    print('')
    print('>> Attacker previously captured valid packet on channel %d' % channel)
    print(' -> Counter candidate: %d (expected: %d)' % (counter_candidate, base_counter))

    # Compute next channel
    total_hops += 1
    next_chan = seq[(counter_candidate+total_hops)%65536]
    print(' -> Attacker switches to channel %d' % next_chan)

    # Wait for packet sent on this channel
    prev_counter = counter
    counter = (counter+1)&0xffff
    print(' INFO: counter before hopping to chan %d: %d' % (next_chan,counter))
    while seq[counter]!=next_chan:
        counter = (counter +1)&0xffff
    print(' INFO: counter when on chan %d: %d' % (next_chan,counter))

    # Deduce hops
    total_hops = counter - ref_counter
    hops = counter - prev_counter

    print(' -> Attacker waited %d hops until a packet arrived on channel %d' % (hops, next_chan))


    # Look in the sequence for every channel followed by next_chan
    if init_candidates is None:
        print('>> No candidates yet, generating a list based on a single measure')
        candidates = []
        for i in range(len(seq)):
            if seq[i]==channel and seq[(i+hops)%(2**16)]==next_chan:
                candidates.append(i)
        print(' -> Initial candidates: %s' % ', '.join(['%d' % c for c in candidates]))
        init_candidates = True
    else:
        print('>> Filtering candidates ...')
        # filter out candidates
        for candidate in candidates:
            if seq[(candidate+total_hops)%(2**16)] != next_chan:
                print(' -> Candidate %d removed' % (candidate))
                candidates.remove(candidate)
        print(' -> Remaining candidates: %s' % ', '.join(['%d' % c for c in candidates]))
        if len(candidates)==1:
            print('>> Found initial counter: %d' % candidates[0])
            print('INFO: Attack required %d hops' % total_hops)
            break
        else:
            print(' -> %d candidates left' % len(candidates))


    channel = next_chan
