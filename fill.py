import pcbnew,sys
for f in sys.argv[1:]:
    b=pcbnew.LoadBoard(f); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(f,b); print("filled",f)
