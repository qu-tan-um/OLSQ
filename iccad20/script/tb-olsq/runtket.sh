#!/bin/sh

for bench in benchmark/paper5/*
do
  python "tket_test.py" "$bench" "ibmqx2" &
done
