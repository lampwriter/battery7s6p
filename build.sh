set -e
cd /workspace/battery7s6p
python3 gen.py
python3 fill.py top/battery7s6p_top.kicad_pcb bot/battery7s6p_bot.kicad_pcb >/dev/null 2>&1
for w in top bot; do
 kicad-cli pcb drc --severity-error --severity-warning --exit-code-violations -o $w/drc.rpt $w/battery7s6p_$w.kicad_pcb >/dev/null 2>&1 || true
 echo "== $w"; grep -E "Found" $w/drc.rpt; grep "^\[" $w/drc.rpt | sort | uniq -c | sort -rn
 for s in top bottom; do kicad-cli pcb render --side $s --width 1600 --height 1200 --quality basic -o renders/${w}_board_${s}.png $w/battery7s6p_$w.kicad_pcb >/dev/null 2>&1; done
done
