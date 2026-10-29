import pcbnew, math, sys, os
from pcbnew import VECTOR2I, FromMM as M
P=20.25; AX=3.0; AY=10.0; NC=7; NR=6
ARR_W=NC*P; ARR_H=NR*P
TX=AX+ARR_W+3.0; W=TX+35.0; H=AY+ARR_H+3.0
OZ=int(os.environ.get('CU_OZ','2'))   # 2 = v1 default; CU_OZ=1 -> 1oz variant
SUF='' if OZ==2 else f'_{OZ}oz'
if OZ==2:
    FUSE_W=1.0; TAP_FUSE_W=0.25; TAP_W=0.5; XTY=62.0
else:   # 1oz: same fuse cross-section (2x width), XT90 moved down so N7 tail spans rows 0-3
    FUSE_W=2.0; TAP_FUSE_W=0.45; TAP_W=0.8; XTY=85.0
POS_PAD=6.0; NEG_PAD=12.0; KEEP_R=6.5
FPLIB='/usr/share/kicad/footprints'
def V(x,y): return VECTOR2I(M(x),M(y))

def build(which):
    b=pcbnew.BOARD()
    ds=b.GetDesignSettings()
    ds.SetCopperLayerCount(2)
    ds.m_TrackMinWidth=M(0.2); ds.m_MinClearance=M(0.2); ds.m_MinThroughDrill=M(0.3)
    ds.m_ViasMinSize=M(0.6); ds.m_ViasMinAnnularWidth=M(0.15); ds.m_HoleClearance=M(0.25)
    ds.m_CopperEdgeClearance=M(0.4); ds.m_HoleToHoleMin=M(0.5)
    ds.m_SolderMaskMinWidth=0
    nets={}
    def net(n):
        if n not in nets:
            ni=pcbnew.NETINFO_ITEM(b,n); b.Add(ni); nets[n]=ni
        return nets[n]
    # outline
    pts=[(0,0),(W,0),(W,H),(0,H)]
    for i in range(4):
        s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(V(*pts[i])); s.SetEnd(V(*pts[(i+1)%4])); s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(M(0.1)); b.Add(s)
    # columns -> (x, orientation, net)
    top = which=='top'
    cols=[]
    for c in range(NC):
        x = AX+c*P+P/2 if top else AX+(NC-1-c)*P+P/2
        g=c+1  # group number
        # group g between N(g-1) and N(g); odd groups have + on top
        pos_here = (g%2==1)==top
        node = g if pos_here else g-1
        cols.append((c,x,pos_here,f"N{node}"))
    def zone(netname,layer,poly,prio=0,keep=False):
        z=pcbnew.ZONE(b); z.SetLayer(layer)
        ol=z.Outline(); ol.NewOutline()
        for p in poly: ol.Append(M(p[0]),M(p[1]))
        if keep:
            z.SetIsRuleArea(True); (getattr(z,"SetDoNotAllowZoneFills",None) or z.SetDoNotAllowCopperPour)(True); z.SetDoNotAllowTracks(False)
            z.SetDoNotAllowVias(False); z.SetDoNotAllowPads(False); z.SetDoNotAllowFootprints(False)
        else:
            z.SetNet(net(netname)); z.SetLocalClearance(M(0.5)); z.SetMinThickness(M(0.25))
            z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL); z.SetAssignedPriority(prio)
        b.Add(z); return z
    def rect(x0,y0,x1,y1): return [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    def circ(cx,cy,r,n=24): return [(cx+r*math.cos(2*math.pi*i/n),cy+r*math.sin(2*math.pi*i/n)) for i in range(n)]
    def via(x,y,n,d=0.9,dr=0.5):
        v=pcbnew.PCB_VIA(b); v.SetPosition(V(x,y)); v.SetWidth(pcbnew.F_Cu,M(d)); v.SetWidth(pcbnew.B_Cu,M(d)); v.SetDrill(M(dr)); v.SetNet(net(n)); b.Add(v)
    def track(a,c,n,w,layer=pcbnew.F_Cu):
        t=pcbnew.PCB_TRACK(b); t.SetStart(V(*a)); t.SetEnd(V(*c)); t.SetWidth(M(w)); t.SetLayer(layer); t.SetNet(net(n)); b.Add(t)
    def path(pts,n,w,layer=pcbnew.F_Cu):
        for i in range(len(pts)-1): track(pts[i],pts[i+1],n,w,layer)
    def text(s,x,y,layer,size=1.5,mirror=False):
        t=pcbnew.PCB_TEXT(b); t.SetText(s); t.SetPosition(V(x,y)); t.SetLayer(layer)
        t.SetTextSize(V(size,size)); t.SetTextThickness(M(size*0.15)); t.SetMirrored(mirror); b.Add(t)
    def silkcirc(x,y,r,layer):
        s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetCenter(V(x,y)); s.SetEnd(V(x+r,y)); s.SetLayer(layer); s.SetWidth(M(0.15)); b.Add(s)
    def cellfp(ref,x,y,n,pos):
        fp=pcbnew.FOOTPRINT(b); fp.SetReference(ref); fp.SetValue('18650_POS' if pos else '18650_NEG')
        fp.SetFPID(pcbnew.LIB_ID('battery7s6p','CELL_POS_CONTACT' if pos else 'CELL_NEG_CONTACT'))
        fp.SetAttributes(pcbnew.FP_SMD|pcbnew.FP_EXCLUDE_FROM_BOM|pcbnew.FP_EXCLUDE_FROM_POS_FILES)
        fp.Reference().SetVisible(False); fp.Value().SetVisible(False)
        b.Add(fp); fp.SetPosition(V(x,y))
        def pad(layers,d):
            p=pcbnew.PAD(fp); p.SetNumber('1'); p.SetShape(pcbnew.PAD_SHAPE_CIRCLE); p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            p.SetSize(V(d,d)); ls=pcbnew.LSET()
            for l in layers: ls.AddLayer(l)
            p.SetLayerSet(ls); fp.Add(p); p.SetPosition(V(x,y)); p.SetNet(net(n))
        if pos:
            pad([pcbnew.B_Cu,pcbnew.B_Mask],POS_PAD); pad([pcbnew.F_Cu],5.5)
        else:
            pad([pcbnew.B_Cu,pcbnew.B_Mask],NEG_PAD); pad([pcbnew.F_Cu],NEG_PAD)
        return fp
    side='TOP' if top else 'BOT'
    ytop=AY-1.0; ybot=AY+ARR_H+1.5
    # F.Cu bus zones grouped by node
    groups={}
    for c,x,pos,n in cols: groups.setdefault(n,[]).append(x)
    for n,xs in groups.items():
        x0=max(min(xs)-P/2+0.5,1.0); x1=min(max(xs)+P/2-0.5,AX+ARR_W+0.5)
        if max(xs)>AX+ARR_W-P:
            x1=AX+ARR_W+0.5
            ty1 = (XTY+4.4) if top else H-1.0
            zone(n,pcbnew.F_Cu,[(x0,ytop),(x1,ytop),(x1,34),(W-1,34),(W-1,ty1),(x1,ty1),(x1,ybot),(x0,ybot)])
            continue
        zone(n,pcbnew.F_Cu,rect(x0,ytop,x1,ybot))
    # B.Cu zones only under negative-end columns
    for c,x,pos,n in cols:
        if not pos: zone(n,pcbnew.B_Cu,rect(x-9.0,AY+0.5,x+9.0,AY+ARR_H-0.5))
    # cells
    k=0
    for c,x,pos,n in cols:
        for r in range(NR):
            y=AY+r*P+P/2; k+=1
            cellfp(f"C{c+1}_{r+1}",x,y,n,pos)
            vr = 1.6 if pos else 3.5
            for i in range(6):
                a=2*math.pi*i/6+math.pi/6; via(x+vr*math.cos(a),y+vr*math.sin(a),n)
            if pos:
                zone(None,pcbnew.F_Cu,circ(x,y,KEEP_R),keep=True)
                track((x,y),(x,y+KEEP_R+1.5),n,FUSE_W)   # fuse link, downward
                silkcirc(x,y,KEEP_R+0.3,pcbnew.F_SilkS)
                silkcirc(x,y,4.6,pcbnew.B_SilkS)   # fish-paper ring marker
                text('+',x+6.4,y-6.4,pcbnew.B_SilkS,1.5,True)
            else:
                text('-',x+7.5,y-7.5,pcbnew.B_SilkS,1.5,True)
        if not pos:
            for r in range(1,NR):
                for dx in (-4,0,4): via(x+dx,AY+r*P,n)
        text(f"G{c+1}{'+' if pos else '-'}",x,AY+ARR_H+1.5,pcbnew.F_SilkS,1.5)
    # mounting holes (interstitial, symmetric)
    for kx,jy in [(1,1),(3,1),(4,1),(6,1),(1,5),(3,5),(4,5),(6,5),(1,3),(6,3)]:
        fp=pcbnew.FootprintLoad(FPLIB+'/MountingHole.pretty','MountingHole_3.2mm_M3')
        fp.SetReference(f"H{kx}{jy}"); fp.Reference().SetVisible(False); fp.SetPosition(V(AX+kx*P,AY+jy*P)); b.Add(fp)
    for i,(hx,hy) in enumerate([(W-6,H-6),(TX+4,H-6)]):
        fp=pcbnew.FootprintLoad(FPLIB+'/MountingHole.pretty','MountingHole_3.2mm_M3')
        fp.SetReference(f"HT{i}"); fp.Reference().SetVisible(False); fp.SetPosition(V(hx,hy)); b.Add(fp)
    # N0 lug (M5 ring terminal, 10AWG jumper between boards)
    lug=pcbnew.FootprintLoad(FPLIB+'/MountingHole.pretty','MountingHole_5.3mm_M5_Pad_Via')
    lug.SetReference('LUG1'); lug.SetValue('N0 M5 LUG'); lug.SetPosition(V(TX+14,H-22)); b.Add(lug)
    for p in lug.Pads(): p.SetNet(net('N0'))
    text('N0 M5 LUG 10AWG',TX+14,H-30,pcbnew.F_SilkS,1.0)
    # tab zones for N0
    def loadfp(lib,name,ref,val,x,y,rot=0):
        fp=pcbnew.FootprintLoad(FPLIB+'/'+lib+'.pretty',name); fp.SetReference(ref); fp.SetValue(val)
        b.Add(fp); fp.SetPosition(V(x,y)); fp.SetOrientationDegrees(rot); return fp
    JY=14.0; JX=TX+5
    chan={}
    if top:
        # XT90 PCB connector
        xt=loadfp('Connector_AMASS','AMASS_XT90PW-M_1x02_P10.90mm_Horizontal','J1','XT90PW-M',W-22,XTY,-90)
        for p in xt.Pads():
            if p.GetNumber()=='1': p.SetNet(net('N7'))
            if p.GetNumber()=='2': p.SetNet(net('N0'))
        for L in (pcbnew.F_Cu,pcbnew.B_Cu):
            if L==pcbnew.B_Cu: zone('N7',L,rect(AX+ARR_W+0.5,34,W-1,XTY+4.4),prio=1)
            zone('N0',L,rect(AX+ARR_W+2.5,XTY+5.4,W-1,H-1.0),prio=1)
        text('+',W-30,XTY,pcbnew.F_SilkS,3); text('-',W-30,XTY+10.9,pcbnew.F_SilkS,3)
        text('XT90 PACK',W-15,XTY-12,pcbnew.F_SilkS,1.5)
        j2=loadfp('Connector_JST','JST_XH_B8B-XH-A_1x08_P2.50mm_Vertical','J2','B8B-XH-A BAL',JX,JY)
        j3=loadfp('Connector_JST','JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical','J3','B4B-XH-A from BOT',JX,JY+12)
        for p in j2.Pads(): p.SetNet(net(f"N{int(p.GetNumber())-1}" if p.GetNumber()!='1' else 'N0_SENSE'))
        for p in j3.Pads(): p.SetNet(net(f"N{2*(int(p.GetNumber())-1)}" if p.GetNumber()!='1' else 'N0_SENSE'))
        text('BAL 1=N0(-) ... 8=N7(+)',JX+8.75,JY-5.5,pcbnew.F_SilkS,1.0)
        text('FROM BOT: N0 N2 N4 N6',JX+8.75,JY+16.5,pcbnew.F_SilkS,0.9)
        # J3 -> J2 even pins (F.Cu), with fuse segments
        ym=[None,19,21,23]
        for i in range(1,4):
            x3=JX+2.5*i; x2=JX+5*i
            path([(x3,JY+12),(x3,ym[i]),(x2,ym[i]),(x2,JY)],f"N{2*i}",TAP_W)
        track((JX,JY+12),(JX,JY),'N0_SENSE',TAP_W)  # N0 sense comes from bottom board via the 4-pin cable
        chan={'N1':6.0,'N3':4.5,'N5':3.0,'N7':1.5}; pin={'N1':1,'N3':3,'N5':5,'N7':7}
    else:
        zone('N0',pcbnew.B_Cu,rect(AX+ARR_W+0.5,34,W-1,H-1.0),prio=1)
        j1=loadfp('Connector_JST','JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical','J1','B4B-XH-A to TOP',JX,JY)
        for p in j1.Pads(): p.SetNet(net(f"N{2*(int(p.GetNumber())-1)}"))
        text('TO TOP J3: N0 N2 N4 N6',JX+8,JY-5.5,pcbnew.F_SilkS,0.9)
        # N0 tap from N0 zone on F at y=JY
        path([(AX+ARR_W,JY),(AX+ARR_W+2,JY)],'N0',TAP_W); path([(AX+ARR_W+2,JY),(AX+ARR_W+5,JY)],'N0',TAP_FUSE_W); path([(AX+ARR_W+5,JY),(JX,JY)],'N0',TAP_W)
        chan={'N2':6.0,'N4':4.5,'N6':3.0}; pin={'N2':1,'N4':2,'N6':3}
    # channel taps: F stub from bus zone (with fuse), via, B.Cu run to pin
    for n,yc in chan.items():
        xs=groups[n]; xstub=sum(xs)/len(xs) if len(xs)>1 else xs[0]+5.0
        if len(xs)>1: xstub = (min(xs)+max(xs))/2   # between the two columns (interstitial)
        px=JX+2.5*pin[n]
        path([(xstub,ytop+3),(xstub,ytop-0.5)],n,TAP_W); path([(xstub,ytop-0.5),(xstub,yc+1.5)],n,TAP_FUSE_W); path([(xstub,yc+1.5),(xstub,yc)],n,TAP_W)
        via(xstub,yc,n)
        path([(xstub,yc),(px,yc),(px,JY)],n,TAP_W,pcbnew.B_Cu)
    if OZ!=2:   # stitch F/B layers of pack-terminal zones
        for yy in range(38,int(XTY)-4,4):
            for xx in (TX+2,TX+6): via(xx,yy,'N7' if top else 'N0',1.0,0.6)
        for yy in (range(int(XTY+9),int(H)-10,4) if top else []):
            for xx in (TX+2,):
                via(xx,yy,'N0',1.0,0.6)
    # notes
    for i,l in enumerate([f"7S6P 18650 {side} v1{SUF}",f"{OZ}oz Cu ENIG","cells face B side","FISH PAPER ON","EVERY + END!"]):
        text(l,TX+17,(H-48 if OZ==2 else 40)+i*2.2,pcbnew.F_SilkS,1.2)
    text("FISH-PAPER RING REQUIRED ON EVERY + CELL END - BARE CANS ARE NEGATIVE",AX+ARR_W/2,AY+ARR_H+1.6,pcbnew.B_SilkS,1.0,True)
    pass
    out=f"/workspace/battery7s6p/{which}{SUF}/battery7s6p_{which}{SUF}.kicad_pcb"
    os.makedirs(os.path.dirname(out),exist_ok=True)
    pcbnew.SaveBoard(out,b)
    print("saved",out, "size", W, H)
for w in ('top','bot'): build(w)
