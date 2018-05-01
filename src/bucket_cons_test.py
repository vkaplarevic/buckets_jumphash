#!/usr/bin/env python

import numpy as np
import ctypes
import random as r
import sys

COUNT = 1500000

# jump hash and that's all we need!
def jump_hash(key, buckets):
    if np.int32(buckets) <= 0:
        buckets = 1
    b = np.int64(-1)
    j = 0
    while j < buckets:
        b = j
        key = ctypes.c_uint64(key * 2862933555777941757 + 1).value
        j = np.int64(np.double(b + 1) * (2147483648.0 / ctypes.c_double((key >> 33) + 1).value))
    return b

def shard_and_bucket(key, bnum, use_jump):
	if use_jump:
		return key % 16, (key % 16) * bnum + jump_hash(key, bnum)

	# Return my peasant hash!
	return key % 16, (key % 16) * bnum + (((key + 51) // 10) * 31) % bnum


def main():
	if len(sys.argv) != 2:
		return

	if sys.argv[1] != 'jump' and sys.argv[1] != 'other':
		print("Command line option can be either: jump or peasant")
		return

	use_jump = sys.argv[1] == 'jump'

	shards = { x: {} for x in range(0,16) }
	for x in range(0, 16):	
		shards[x] = {}
		for b in range(0, 6):
			shards[x][x*6 + b] = 0

	# So, after this, each shard contains 6 buckets
	# and every single bucket has unique tag...
	miss = 0
	for k in range(0, COUNT):
		if r.randint(0, 9) == 1:
			miss += 1
			continue

		shard, bucket = shard_and_bucket(k, 6, use_jump)
		shards[shard][bucket] += 1

	print("miss:", miss, "\n")

	# Let's print this. All buckets should have
	# roughly the same size with the jump hash function.
	bucket_values = []
	for s in range(0, 16):
		print("shard:", s)
		for b in shards[s].keys():
			print("    b" +  str(b) + ":" , shards[s][b])
			bucket_values.append(shards[s][b])	

	bucket_values.sort()

	print("\nmax:", max(bucket_values))
	print("min:", min(bucket_values))
	print("mean:", np.mean(bucket_values))
	print("median:", (bucket_values[48] + bucket_values[47]) / 2)
	print("std. dev:", np.std(bucket_values))


main()


