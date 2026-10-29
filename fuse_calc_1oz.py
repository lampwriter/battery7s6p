import math
T1=35e-3/25.4e-3  # 1oz thickness mil (1.378)
def area(w,t): return w/0.0254*t
def dT(I,w,t): return (I/(0.048*area(w,t)**0.725))**(1/0.44)
def ond(w,t,tt,Ta=25,Tm=1083): return area(w,t)*4/math.pi*math.sqrt(math.log10((Tm-Ta)/(234+Ta)+1)/(33*tt))
T2=2*T1
L=["7S6P 1oz variant - current check (IPC-2221 external, dT=20C target), 30 A pack current",
"Need for 30 A @ dT20: 21.5 mm on 1oz single layer (10.7 mm on 2oz).",""]
paths=[("Interior series-node zones (midline between columns, minus 3 M3 holes), F only",30,112),
("Pos column at cell row (N7 col, gaps beside 13mm keepout), worst: row5 current",5,7.2),
("N7: rows4+5 into XT90 tail, keepout-to-corner neck (1oz layout, XT90 at y=85)",10,8.2),
("N7 tail to XT90 (x=148..182, y 34..89.4), F only (B stitched adds more)",30,55),
("N0 top zone (y 90.4..133.5) F+B each, per layer half current",15,42),
("N0 bottom tail (y 34..133.5) F only, neg column (12mm pads, no keepout)",30,97),
("XT90 pad 7.2mm, zone wrap ~3/4 perimeter x 2 layers",30,34),
("M5 lug pad 10.6mm, full perimeter x 2 layers",30,66),
("For reference: v1 layout N7 neck beside row2 (XT90 at y=62)",15,5.6)]
for n,I,w in paths: L.append(f"{n}: {I} A over {w} mm -> dT 1oz {dT(I,w,T1):5.1f} C (2oz {dT(I,w,T2):4.1f} C)")
L+=["  -> v1 layout would be ~%.0f C at 1oz: NOT ok; fixed by moving XT90 23 mm down (N7 tail now covers rows 0-3)."%dT(15,5.6,T1),"",
"Cell fuse: 2oz 1.0 mm vs 1oz 2.0 mm (same 70 um*mm cross-section):"]
for lab,w,t in (("2oz 1.0mm",1.0,T2),("1oz 2.0mm",2.0,T1)):
    L.append(f"  {lab}: cont@dT20 {(0.048*20**0.44*area(w,t)**0.725):.1f} A; Onderdonk melt 10s/1s/0.1s/10ms: "+" ".join(f"{ond(w,t,x):.1f}A" for x in (10,1,.1,.01)))
L.append("  exposed fuse length unchanged ~3.75 mm (island r2.75 to keepout r6.5); blow current ~same (thin 1oz conducts slightly less heat away -> marginally lower).")
for lab,w,t in (("2oz 0.25mm",0.25,T2),("1oz 0.45mm",0.45,T1)):
    L.append(f"  Balance tap fuse {lab}: cont@dT20 {(0.048*20**0.44*area(w,t)**0.725):.2f} A; melt 1s {ond(w,t,1):.1f}A 10ms {ond(w,t,.01):.1f}A")
L.append("Balance tap traces 0.8 mm (was 0.5). Stitching vias (1.0/0.6) tie F/B on N7 tail and N0 zone.")
open('fuse_calc_1oz.txt','w').write("\n".join(L)+"\n"); print("\n".join(L))
