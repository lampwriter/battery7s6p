import math
def dT(I,w_mm,oz=1):  # IPC-2221 external
    A=w_mm/0.0254*1.378*oz; return (I/(0.048*A**0.725))**(1/0.44)
out=[]
p=out.append
p("CURRENT CHECK v1.2 (1oz, IPC-2221 external, target dT<=20C)")
for name,I,w in [("Column-to-column bridge, typical (one cell's 5 A), 10 mm F only",5,10),
                 ("Column-to-column bridge, 2x unequal sharing (10 A), 10 mm",10,10),
                 ("Column-to-column bridge, 3x (15 A), 10 mm",15,10),
                 ("All 6 bridges of one column line together, 30 A over 70 mm",30,70),
                 ("N7 (top)/N0 (bot) end column, rows4+5 -> tail via row-line-4 bridge, 10 A over 15 mm",10,15),
                 ("Row-line bridge inside a column (cell-to-cell sharing), 5 A over 10 mm",5,10)]:
    p(f"  {name}: dT {dT(I,w):5.1f} C")
p("  Unchanged from v1.1 (copper not touched): N7 tail 4.3 C, XT90 pad 9.4 C, N0 zones 1.4-1.7 C, M5 lug 3.2 C, cell fuses identical.")
p("")
p("FLEXURE / FORCE")
E=20000.0; t=0.8; b=10.0; Leff=4.0
EI=E*b*t**3/12; kr=EI/Leff
p(f"  Bridge (10 mm wide, 0.8 mm FR4, eff. hinge length {Leff} mm): EI={EI:.0f} N*mm^2, rot. stiffness {kr:.0f} N*mm/rad")
for dl in (0.1,0.2,0.3):
    th=dl/P_ if (P_:=20.25) else 0; F=kr*th/10*4
    p(f"   neighbour cell {dl} mm shorter -> up to ~{F:.1f} N lost to 4 bridges")
EI16=E*b*1.6**3/12; p(f"  (same bridge in 1.6 mm FR4 would be {EI16/EI:.0f}x stiffer -> why v1.2 is 0.8 mm)")
cfd=67e3; area=20.25**2-4*math.pi*3.25**2/4
F0=cfd*area*1e-6; k=F0/(0.25*3.18)
p(f"  Foam: BISCO HT-800 3.18 mm (1/8in), CFD 67 kPa typ (41-97 spec) @25%; area/cell {area:.0f} mm^2")
p(f"   -> nominal contact force {F0:.1f} N/cell at 0.80 mm squeeze (spec range {41e3*area*1e-6:.0f}-{97e3*area*1e-6:.0f} N); ~{k:.0f} N/mm")
for dl in (-0.3,-0.1,0.1,0.3):
    p(f"   cell {dl:+.1f} mm vs nominal: ~{F0+k*dl:.0f} N (foam squeeze {(0.795+dl)/3.18*100:.0f}%)")
Ftot=42*F0; p(f"  Clamp load per end plate: 42 x {F0:.1f} = {Ftot:.0f} N ({Ftot/4.448:.0f} lbf); 12 rods -> {Ftot/12:.0f} N/rod (M4 A2-70 proof ~6.2 kN: >60x margin)")
q=Ftot/(141.75*121.5); D=69000*6.35**3/(12*0.91); w=0.00406*q*40.5**4/D
p(f"  6.35 mm 6061 plate, 40.5 mm rod grid: pressure {q*1000:.0f} kPa, deflection ~{w*1000:.2f} um (negligible); 12 mm Baltic-birch ply also fine (~{w*69000/8000*(6.35/12)**3*1000:.2f} um)")
Rc=0.002; p(f"  Contact loss @30 A (6 x 5 A/cell), assume {Rc*1000:.0f} mOhm per ENIG-to-Ni contact at ~25 N: 84 contacts x 25 A^2 x R = {84*25*Rc:.1f} W")
L=65.1; gap=L+2*0.8+2*3.18*0.75
p(f"  Stack: plate | foam 3.18->2.39 | PCB 0.8 | cell {L} (measure yours) | PCB 0.8 | foam | plate -> tube length {gap:.2f} mm")
open('calc_v12.txt','w').write('\n'.join(out)); print('\n'.join(out))
