#!/bin/sh

# for bench in benchmark/paper/*
# do
#   s=${bench##*/}
#   echo "$s"
#   s=${s%.*}
#   echo "$s"
#   python "../TriQ/ir2dag.py" "$bench" "result/paper/${s}_ibmq14_triq.in" &
# done

for infile in ../ExQuS/result/paper/*.in
do
  ./triq "$infile" "${infile%.*}_ibmq14_triq_fidelity.qasm" | tee "${infile%.*}_ibmq14_triq_fidelity" &
done
