# v1.2 drill/cut template for HDPE holders, backing plates and foam (same pattern both ends; symmetric)
import ezdxf, math
P=20.25; AX=3.0; AY=10.0; NC=7; NR=6; W=182.75; H=134.5; TX=AX+NC*P+3.0
ROD_PTS=[(c,r) for c in (1,3,4,6) for r in (1,3,5)]
def Y(y): return H-y   # DXF y-up, origin = board lower-left corner
d=ezdxf.new('R2010'); d.units=ezdxf.units.MM; m=d.modelspace()
for n,col in [('PCB_OUTLINE',7),('CELL_HOLES_18p6',3),('CELL_CENTERS',2),('ROD_HOLES_6p5',1),('ARRAY_EDGE',5),('PCB_M3_HOLES',6),('NOTES',7)]: d.layers.add(n,color=col)
m.add_lwpolyline([(0,0),(W,0),(W,H),(0,H)],close=True,dxfattribs={'layer':'PCB_OUTLINE'})
m.add_lwpolyline([(AX,Y(AY)),(AX+NC*P,Y(AY)),(AX+NC*P,Y(AY+NR*P)),(AX,Y(AY+NR*P))],close=True,dxfattribs={'layer':'ARRAY_EDGE'})
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}"><rect x="0" y="0" width="{W}" height="{H}" fill="none" stroke="black" stroke-width="0.2"/>']
for c in range(NC):
    for r in range(NR):
        x=AX+c*P+P/2; y=AY+r*P+P/2
        m.add_circle((x,Y(y)),9.3,dxfattribs={'layer':'CELL_HOLES_18p6'}); m.add_point((x,Y(y)),dxfattribs={'layer':'CELL_CENTERS'})
        svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="9.3" fill="none" stroke="green" stroke-width="0.2"/><circle cx="{x:.3f}" cy="{y:.3f}" r="0.3" fill="green"/>')
for c,r in ROD_PTS:
    x=AX+c*P; y=AY+r*P
    m.add_circle((x,Y(y)),3.25,dxfattribs={'layer':'ROD_HOLES_6p5'})
    svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="3.25" fill="none" stroke="red" stroke-width="0.25"/>')
for hx,hy in [(W-6,H-6),(TX+4,H-6)]:
    m.add_circle((hx,Y(hy)),1.6,dxfattribs={'layer':'PCB_M3_HOLES'})
    svg.append(f'<circle cx="{hx}" cy="{hy}" r="1.6" fill="none" stroke="magenta" stroke-width="0.2"/>')
m.add_text('battery7s6p v1.2 template, mm, origin=PCB lower-left. Cell pitch 20.25. Rods: 12x 6.5mm',dxfattribs={'layer':'NOTES','height':2.5}).set_placement((2,-6))
d.saveas('fab_v12/battery7s6p_v12_drill_template.dxf')
svg.append('</svg>'); open('fab_v12/battery7s6p_v12_drill_template.svg','w').write('\n'.join(svg))
print('rods:',[(round(AX+c*P,3),round(AY+r*P,3)) for c,r in ROD_PTS])
