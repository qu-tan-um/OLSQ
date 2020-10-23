for bench in benchmark/paper5/*
do
  s=${bench##*/}
  s=${s%.*}
  python -u "newsmt.py" "$bench" "ibmqx2" "swap" | tee "result/paper/${s}_ibmqx2_tbelsq_swap" &
  python -u "newsmt.py" "$bench" "ibmqx2" "fidelity" | tee "result/paper/${s}_ibmqx2_tbelsq_fidelity" &
done
