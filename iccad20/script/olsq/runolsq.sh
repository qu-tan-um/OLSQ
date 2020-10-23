for bench in benchmark/paper5/*
do
  s=${bench##*/}
  s=${s%.*}
  python -u "smt.py" "$bench" "ibmqx2" "swap" | tee "result/paper/${s}_ibmqx2_elsq_swap" &
  python -u "smt.py" "$bench" "ibmqx2" "depth" | tee "result/paper/${s}_ibmqx2_elsq_depth" &
  python -u "smt.py" "$bench" "ibmqx2" "fidelity" | tee "result/paper/${s}_ibmqx2_elsq_fidelity" &
done
python -u "smt.py" "benchmark/paper5/tof_3_after_heavy.qasm" "grid2by3" "swap" | tee "result/paper/tof_3_after_heavy_grid2by3_elsq_swap" &
python -u "smt.py" "benchmark/paper5/tof_3_after_heavy.qasm" "grid2by3" "depth" | tee "result/paper/tof_3_after_heavy_grid2by3_elsq_depth" &
python -u "smt.py" "benchmark/paper5/tof_3_after_heavy.qasm" "grid2by3" "fidelity" | tee "result/paper/tof_3_after_heavy_grid2by3_elsq_fidelity" &
python -u "smt.py" "benchmark/paper5/tof_3_after_heavy.qasm" "grid2by4" "swap" | tee "result/paper/tof_3_after_heavy_grid2by4_elsq_swap" &
python -u "smt.py" "benchmark/paper5/tof_3_after_heavy.qasm" "grid2by4" "depth" | tee "result/paper/tof_3_after_heavy_grid2by4_elsq_depth" &
python -u "smt.py" "benchmark/paper5/tof_3_after_heavy.qasm" "grid2by4" "fidelity" | tee "result/paper/tof_3_after_heavy_grid2by4_elsq_fidelity" &
python -u "smt.py" "benchmark/paper5/mod5_4_after_heavy.qasm" "grid2by3" "swap" | tee "result/paper/mod5_4_after_heavy_grid2by3_elsq_swap" &
python -u "smt.py" "benchmark/paper5/mod5_4_after_heavy.qasm" "grid2by3" "depth" | tee "result/paper/mod5_4_after_heavy_grid2by3_elsq_depth" &
python -u "smt.py" "benchmark/paper5/mod5_4_after_heavy.qasm" "grid2by3" "fidelity" | tee "result/paper/mod5_4_after_heavy_grid2by3_elsq_fidelity" &
python -u "smt.py" "benchmark/paper5/mod5_4_after_heavy.qasm" "grid2by4" "swap" | tee "result/paper/mod5_4_after_heavy_grid2by4_elsq_swap" &
python -u "smt.py" "benchmark/paper5/mod5_4_after_heavy.qasm" "grid2by4" "depth" | tee "result/paper/mod5_4_after_heavy_grid2by4_elsq_depth" &
python -u "smt.py" "benchmark/paper5/mod5_4_after_heavy.qasm" "grid2by4" "fidelity" | tee "result/paper/mod5_4_after_heavy_grid2by4_elsq_fidelity" &
python -u "smt.py" "benchmark/queko/16QBT_05CYC_TFL_0.qasm" "aspen4" "swap" | tee "result/paper/16QBT_05CYC_TFL_0_aspen4_elsq_swap" &
python -u "smt.py" "benchmark/queko/16QBT_05CYC_TFL_0.qasm" "aspen4" "depth" | tee "result/paper/16QBT_05CYC_TFL_0_aspen4_elsq_depth" &
python -u "smt.py" "benchmark/queko/16QBT_05CYC_TFL_0.qasm" "aspen4" "fidelity" | tee "result/paper/16QBT_05CYC_TFL_0_aspen4_elsq_fidelity" &
python -u "smt.py" "benchmark/queko/16QBT_10CYC_TFL_0.qasm" "aspen4" "swap" | tee "result/paper/16QBT_10CYC_TFL_0_aspen4_elsq_swap" &
python -u "smt.py" "benchmark/queko/16QBT_10CYC_TFL_0.qasm" "aspen4" "depth" | tee "result/paper/16QBT_10CYC_TFL_0_aspen4_elsq_depth" &
python -u "smt.py" "benchmark/queko/16QBT_10CYC_TFL_0.qasm" "aspen4" "fidelity" | tee "result/paper/16QBT_10CYC_TFL_0_aspen4_elsq_fidelity" &
