try:
	import re


	# query for file paths.
	path_to_extended_ovr = r"extended-overrides.txt"
	path_to_tdecimate_ovr = r"tdecimate-overrides.txt"
	gui_title = "Generation of TDecimater overrides"
	gui_db = [ \
		[ \
			"Path to extended overrides",
			(path_to_extended_ovr, "Plain text (*.txt)|*.txt"),
			"file_open",
		], [ \
			"Path to TDecimate overrides",
			(path_to_tdecimate_ovr, "Plain text (*.txt)|*.txt"),
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
			path_to_extended_ovr, path_to_tdecimate_ovr = options
		break


	# loading of extended overrides.
	extended_ovrs = []
	with open(path_to_extended_ovr, "rt", buffering = 65536) as fh:
		extended_ovr_re = re.compile("^\s*?(?:(\d+?)\s*?,\s*?(\d+?)\s*?(v|vc|f|fc|ii|i|e|o)|(\d+?)\s*?(v|vc|f|fc|i|e|o)\s*?([-+]\s*?\d+?)?)?\s*?(?:#.*)?\s*?$")
		for line in fh:
			found = extended_ovr_re.search(line)
			if found and found.group(1):
				extended_ovrs.append((int(found.group(1)), int(found.group(2)), found.group(3)))


	# saving of TDecimate overrides.
	with open(path_to_tdecimate_ovr, "wt", buffering = 65536) as fh:
		prev_b = -255
		curr_a = 0
		curr_b = 0
		for ovr in extended_ovrs:
			a, b, s = ovr

			# shifting of boundaries of defind sections to nearest telecined GOPs.
			if a % 5 != 0:
				# move closer to frame #0.
				curr_a = a - a % 5
			if b % 5 != 4:
				# move closer to frame #framecount-1.
				# alternative to if (b + 1) % 5 != 0: b += 5 - (b + 1) % 5.
				curr_b = b + 4 - b % 5

			# detection of collisions and saving.
			if s == "f" or s == "fc":
				fh.write("{:d},{:d} {}".format(curr_a, curr_b, "f" if curr_b < curr_a else "f # Collision with previous range. Range before adjustment: {:d},{:d}.".format(a, b)))
			elif s == "v" or s == "vc" or s == "i" or s == "ii" or s == "e" or s == "o":
				fh.write("{:d},{:d} {}\n".format(curr_a, curr_b, "v" if curr_b < curr_a else "v # Collision with previous range. Range before adjustment: {:d},{:d}.".format(a, b)))

			prev_b = curr_b
except Exception as e:
	print(e)
