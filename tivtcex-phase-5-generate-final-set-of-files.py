try:
	import re


	# query for file paths.
	path_to_extended_ovr = "extended-overrides.txt"
	path_to_timecodes = "tdecimate-timecodes.txt"
	path_to_org_frames = "tdecimate-original-frame-sids.txt"
	path_to_edl = "edl.txt"
	path_to_timestamps = "timestamps.txt"
	gui_title = "Generation of EDL and timestamps"
	gui_db = [ \
		[ \
			"Path to extended overrides",
			(path_to_extended_ovr, "Plain text (*.txt)|*.txt"),
			"file_open",
		], [ \
			"Path to TDecimate timecodes",
			(path_to_timecodes, "Plain text (*.txt)|*.txt"),
			"file_open",
		], [ \
			"Path to pre-TDecimate frame SIDs",
			(path_to_org_frames, "Plain text (*.txt)|*.txt"),
			"file_open",
		], [ \
			"Path to EDL",
			(path_to_edl, "Plain text (*.txt)|*.txt"),
			"file_save",
		], [ \
			"Path to timestamps",
			(path_to_timestamps, "Plain text (*.txt)|*.txt"),
			"file_save",
		]
	]
	while True:
		options = avsp.GetTextEntry( \
			title = gui_title,
			message = [d[0] for d in gui_db],
			default = [d[1] for d in gui_db],
			types = [d[2] for d in gui_db],
			width = 300,
		)
		if options:
			path_to_extended_ovr, path_to_timecodes, path_to_org_frames, path_to_edl, path_to_timestamps = options
		break


	# loading of TDecimate timecodes.
	timecodes = []
	with open(path_to_timecodes, "rt", buffering = 65536) as fh:
		tc_re = re.compile("^\d+?\.\d+?$")
		for line in fh:
			if tc_re.match(line):
				timecodes.append(float(line))


	# loading of log with pre-TDecimate frame SIDs.
	# they are generated by patched TDecimate with argument "orgOut".
	with open(path_to_org_frames, "rt", buffering = 65536) as fh:
		org_frames = tuple(int(line) for line in fh)


	# mapping of content types to post-TDecimate frames.
	content_types = {}
	with open(path_to_extended_ovr, "rt", buffering = 65536) as fh:
		extended_ovr_re = re.compile("^\s*?(?:(\d+?)\s*?,\s*?(\d+?)\s*?(v|vc|f|fc|ii|i|e|o)|(\d+?)\s*?(v|vc|f|fc|i|e|o)\s*?([-+]\s*?\d+?)?)?\s*?(?:#.*)?\s*?$")
		for line in fh:
			found = extended_ovr_re.search(line)
			if found:
				if found.group(1):
					a = int(found.group(1))
					b = int(found.group(2))
					s = found.group(3)
					for f in xrange(a, b + 1):
						content_types[f] = (s, 0)
				elif found.group(4):
					f = int(found.group(4))
					s = found.group(5)
					n = int(found.group(6)) if found.group(6) else 0
					content_types[f] = (s, n)


	# construction of new EDL and timestamps.
	# essentially we map content types from original clip
	# to decimated clip using stats produced by TDecimate(orgOut=path).
	# each content type SID corresponds to clip SID supplied to EDL().
	edl = []
	timestamps = []
	i_fl = 1.0 / (60.0 / 1001.0) # length of 1 interlaced frame.
	for decimated_frame_sid, original_frame_sid in enumerate(org_frames):
		if original_frame_sid in content_types:
			content_type, offset = content_types[original_frame_sid]
		else:
			content_type = "v" # in our case has the same effect as "f".
			offset = 0

		# original TIVTC clip.
		if content_type == "v" or content_type == "f":
			edl.append((0, original_frame_sid + offset) * 6)
			timestamps.append(timecodes[decimated_frame_sid])

		# decombed TIVTC clip.
		elif content_type == "vc" or content_type == "fc":
			edl.append((1, original_frame_sid + offset) * 6)
			timestamps.append(timecodes[decimated_frame_sid])

		# blend-deinterlaced clip.
		elif content_type == "i":
			edl.append((2, original_frame_sid + offset) * 6)
			timestamps.append(timecodes[decimated_frame_sid])

		# bob-deinterlaced clip.
		# offsets not supported.
		elif content_type == "ii":
			tc = timecodes[decimated_frame_sid]

			edl.append((3, original_frame_sid * 2) * 6)
			timestamps.append(tc)

			edl.append((3, original_frame_sid * 2 + 1) * 6)
			timestamps.append(tc + i_fl)

		# extrapolated even field (from bob deinterlaced clip).
		elif content_type == "e":
			edl.append((4, original_frame_sid + offset) * 6)
			timestamps.append(timecodes[decimated_frame_sid])

		# extrapolated odd field (from bob deinterlaced clip).
		elif content_type == "o":
			edl.append((5, original_frame_sid + offset) * 6)
			timestamps.append(timecodes[decimated_frame_sid])


	# saving of EDL file.
	with open(path_to_edl, "wt", buffering = 65536) as fh:
		for config in edl:
			fh.write(";".join(str(v) for v in config))
			fh.write("\n")


	# saving of timestamps file.
	with open(path_to_timestamps, "wt", buffering = 65536) as fh:
		fh.write("# timestamp format v2\n")
		for ts in timestamps:
			fh.write("{:.6f}\n".format(ts))
except Exception as e:
	print(e)
