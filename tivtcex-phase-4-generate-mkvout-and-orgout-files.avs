LoadPlugin("dgdecode.dll")
LoadPlugin("tivtc.dll")


MPEG2Source("file.d2v")


TFM(mode = 0, pp = 0, input = "tfm-metrics.txt")
TDecimate(mode = 5, hybrid = 2, tcfv1 = False, input = "tdecimate-metrics.txt", tfmIn = "tfm-metrics.txt", mkvOut = "tdecimate-timecodes.txt", orgOut = "tdecimate-original-frame-sids.txt")
