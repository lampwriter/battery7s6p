set -e
cd /workspace/battery7s6p
CU_OZ=1 python3 gen.py
python3 fill.py top_1oz/battery7s6p_top_1oz.kicad_pcb bot_1oz/battery7s6p_bot_1oz.kicad_pcb >/dev/null 2>&1
for w in top bot; do
 kicad-cli pcb drc --severity-error --severity-warning --exit-code-violations -o ${w}_1oz/drc.rpt ${w}_1oz/battery7s6p_${w}_1oz.kicad_pcb >/dev/null 2>&1 || true
 echo "== $w"; grep -E "Found" ${w}_1oz/drc.rpt; grep "^\[" ${w}_1oz/drc.rpt | sort | uniq -c | sort -rn
 for s in top bottom; do kicad-cli pcb render --side $s --width 1600 --height 1200 --quality basic -o renders/${w}_1oz_board_${s}.png ${w}_1oz/battery7s6p_${w}_1oz.kicad_pcb >/dev/null 2>&1; done
done
