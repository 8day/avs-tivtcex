LoadPlugin("dgdecode.dll")
LoadPlugin("tivtc.dll")
LoadPlugin("vinverse.dll")
LoadCPlugin("yadif.dll")
LoadPlugin("edl.dll")


src = MPEG2Source("file.d2v")
fm = src.TFM(mode = 0, pp = 0, hint = False, input = "tfm-metrics.txt")
decomb = fm.Vinverse()
blend_deinter = BlankClip(fm)
bob_deinter = src.YADIF(1)
extra_even = bob_deinter.SelectEvery(2, 0)
extra_odd = bob_deinter.SelectEvery(2, 1)


EDL( \
    fm.SeparateFields(), \
    decomb.SeparateFields(), \
    blend_deinter.SeparateFields(), \
    bob_deinter.SeparateFields(), \
    extra_even.SeparateFields(), \
    extra_odd.SeparateFields(), \
    path_to_edl = "edl.txt" \
)
Weave()
