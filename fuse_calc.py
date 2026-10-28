import math
OZ2_MIL=2.756  # 2 oz = 70 um
def ipc_ext(w_mm,dT):
    A=w_mm/0.0254*OZ2_MIL
    return 0.048*dT**0.44*A**0.725
def onderdonk(w_mm,t,Ta=25,Tm=1083):
    A_mil2=w_mm/0.0254*OZ2_MIL
    cm=A_mil2*4/math.pi
    return cm*math.sqrt(math.log10((Tm-Ta)/(234+Ta)+1)/(33*t))
print("width_mm | IPC-2221 ext I@dT20 | I@dT40 | Onderdonk melt I @10s 1s 0.1s 10ms")
for w in (0.5,0.6,0.7,0.8,1.0,1.2):
    print(f"{w:4.2f} | {ipc_ext(w,20):5.1f} A | {ipc_ext(w,40):5.1f} A | "+"  ".join(f"{onderdonk(w,t):6.1f}A" for t in (10,1,0.1,0.01)))
print("tap fuse 0.25mm:", round(ipc_ext(0.25,20),2),"A cont @dT20;", [round(onderdonk(0.25,t),1) for t in (10,1,0.1,0.01)])
