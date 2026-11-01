set -e
cd /workspace/battery7s6p
V12=1 python3 gen.py
python3 fill.py top_v12/battery7s6p_top_v12.kicad_pcb bot_v12/battery7s6p_bot_v12.kicad_pcb >/dev/null 2>&1
for w in top bot; do
 kicad-cli pcb drc --severity-error --severity-warning --exit-code-violations -o ${w}_v12/drc.rpt ${w}_v12/battery7s6p_${w}_v12.kicad_pcb >/dev/null 2>&1 || true
 echo "== $w"; grep -E "Found" ${w}_v12/drc.rpt; grep "^\[" ${w}_v12/drc.rpt | sort | uniq -c | sort -rn
 for s in top bottom; do kicad-cli pcb render --side $s --width 1600 --height 1200 --quality basic -o renders/${w}_v12_board_${s}.png ${w}_v12/battery7s6p_${w}_v12.kicad_pcb >/dev/null 2>&1; done
done
