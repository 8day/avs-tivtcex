LoadPlugin("dgdecode.dll")
LoadPlugin("tivtc.dll")


MPEG2Source("file.d2v")


TFM(mode = 0, pp = 0, input = "tfm-metrics.txt")


# favourite filter chain for analysis of hybrid video.
# if you don't know what to use, try Histogram("luma").
