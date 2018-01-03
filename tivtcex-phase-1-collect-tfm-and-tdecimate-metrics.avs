LoadPlugin("dgdecode.dll")
LoadPlugin("tivtc.dll")


MPEG2Source("file.d2v")


TFM(mode = 0, pp = 0, output = "tfm-metrics.txt")
TDecimate(mode = 4, output = "tdecimate-metrics.txt")
