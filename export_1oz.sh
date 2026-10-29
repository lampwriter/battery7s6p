set -e
cd /workspace/battery7s6p; mkdir -p fab_1oz
for w in top bot; do
 pcb=${w}_1oz/battery7s6p_${w}_1oz.kicad_pcb; g=fab_1oz/gerbers_${w}_1oz; rm -rf $g; mkdir -p $g
 kicad-cli pcb export gerbers --layers F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,F.Paste,B.Paste,Edge.Cuts --no-protel-ext -o $g/ $pcb >/dev/null
 kicad-cli pcb export drill --format excellon --excellon-separate-th --generate-map --map-format gerberx2 -o $g/ $pcb >/dev/null
 python3 -c "import shutil;shutil.make_archive('fab_1oz/battery7s6p_${w}_1oz_gerbers','zip','$g')"
 kicad-cli pcb export pos --format csv --units mm --side both --exclude-dnp -o fab_1oz/raw_pos_$w.csv $pcb >/dev/null
done
python3 - <<'PY'
import csv
lcsc={'XT90PW-M':('C3040689','AMASS XT90PW-M (XT90 PCB male, right-angle)'),'B8B-XH-A BAL':('C157972','JST B8B-XH-A(LF)(SN)'),
 'B4B-XH-A from BOT':('C144395','JST B4B-XH-A(LF)(SN)'),'B4B-XH-A to TOP':('C144395','JST B4B-XH-A(LF)(SN)')}
for w in ('top','bot'):
    rows=list(csv.DictReader(open(f'fab_1oz/raw_pos_{w}.csv')))
    rows=[r for r in rows if r['Val'] in lcsc]
    with open(f'fab_1oz/battery7s6p_{w}_1oz_BOM_JLCPCB.csv','w',newline='') as f:
        c=csv.writer(f); c.writerow(['Comment','Designator','Footprint','LCSC Part #'])
        for r in rows: c.writerow([lcsc[r['Val']][1],r['Ref'],r['Package'],lcsc[r['Val']][0]])
    with open(f'fab_1oz/battery7s6p_{w}_1oz_CPL_JLCPCB.csv','w',newline='') as f:
        c=csv.writer(f); c.writerow(['Designator','Mid X','Mid Y','Layer','Rotation'])
        for r in rows: c.writerow([r['Ref'],r['PosX']+'mm',r['PosY']+'mm','Top' if r['Side']=='top' else 'Bottom',r['Rot']])
    print(w,[ (r['Ref'],r['Val']) for r in rows])
PY
ls -la fab_1oz
