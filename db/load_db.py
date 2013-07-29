#!/usr/bin/env python

import csv
from redis import StrictRedis
from pyreBloom import pyreBloom
from subprocess import Popen, PIPE
from os import remove as rm


def split_csv(line):
  if not line:
    return []
  c = csv.reader([line], skipinitialspace=True)
  return list(c)[0]


def get_redis_protocol(*args):
  # number of args
  s = "*%d%s%s" % (len(args), chr(13), chr(10))
  for arg in args:
    s += "$%d%s%s" % (len(arg), chr(13), chr(10))
    s += "%s%s%s" % (arg, chr(13), chr(10))

  return s


redis = StrictRedis(host='localhost', port=6379, db=0)
redis.flushdb()

bloom = pyreBloom('gene_symbols', 100000, 0.01)

# iterate through the file, each line is a gene symbol
# generate the redis request protocol for inserting the data
# http://redis.io/topics/protocol
command = ""
for row in csv.DictReader(open('hgnc_complete_set.txt'), delimiter="\t"):

  # skip non-approved genes
  if row["Status"] != "Approved":
    continue

  symbol = row["Approved Symbol"]
  if len(symbol) == 1:
    print "SKIPPING %s: SYMBOL TOO SHORT" % (symbol)
    continue
  if symbol == "":
    print "WARNING: NO SYMBOL"
  prev_symbols = split_csv(row["Previous Symbols"])
  other_symbols = split_csv(row["Synonyms"])
  prev_symbols.extend(other_symbols)

  bloom.add(symbol)
  bloom.extend(prev_symbols)

  refseq_ids = row["RefSeq IDs"]
  pubmed_ids = row["Pubmed IDs"]

  # map previous symbols to the current symbol
  for prev_sym in prev_symbols:
    command += get_redis_protocol("SET", prev_sym, symbol)

  # map the current symbol to itsself
  command += get_redis_protocol("SET", symbol, symbol)

  # set a hash from the current symbol to refseq and pubmed
  if refseq_ids and pubmed_ids:
    command += get_redis_protocol("HMSET", "h_%s" % (symbol),
                                  "refseq", refseq_ids,
                                  "pubmed", pubmed_ids)
  elif refseq_ids:
    command += get_redis_protocol("HSET", "h_%s" % (symbol),
                                  "refseq", refseq_ids)
  elif pubmed_ids:
    command += get_redis_protocol("HSET", "h_%s" % (symbol),
                                  "pubmed", pubmed_ids)

# write commands to a file to pipe to redis-cli
datafile = open("data.txt", "w")
datafile.write(command)
datafile.close()

# perform data insertion
process = Popen("cat data.txt | redis-cli --pipe",
                stdout=PIPE, stderr=PIPE, shell=True)
stdout, stderr = process.communicate()
stdout = stdout.split("\n")

if len(stdout) == 4 and "errors: 0," in stdout[2]:
  print "No errors."
  print "%d keys successfully inserted." % (len(redis.keys()) - 1)
  rm(datafile.name)
else:
  print "Errors detected."
  print "Standard Out:"
  print stdout
  print "Standard Error:"
  print stderr
  print "Check data.txt for redis command protocols generated"
