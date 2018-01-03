## prerequisites
- AviSynth 2.5+;
- AvsP or AvsPmod;
- EDL plugin for AviSynth;
- TIVTC plugin for AviSynth with version 1.0.5.1, or the one that has argument "orgOut".


## workflow
1. play `tivtcex-phase-1-*.avs` in VirtualDub/AVSMeter to collect metrics for TFM and TDecimate;
2. analyze field-matched clip as shown in `tivtcex-phase-2-*.avs` and create extended overrides:
	- save *ranges of frames* that need special processing using these specifiers:
		- `v`/`f` -- to mark video/film sections;
		- `vc`/`fc` -- to mark combed video/film sections;
		- `i` -- to mark blend-deinterlaced sections;
		- `ii` -- to mark bob-deinterlaced sections;
		- `e` -- to mark sections with extrapolated even fields from src/undecimated clip;
		- `o` -- to mark sections with extrapolated odd fields from src/undecimated clip.
	- save *frames* that need special processing using any of the specifiers used for ranges, excluding `ii`.  you can add `±N` to specify offset in relation to current frame within clip that will be mapped to specifier;
	- decimation pattern is not supported and must be inserted manually after TDecimate overrides will be generated;
	- ranges use classic TIVTC format `N,M`;
	- tabs/spaces are allowed in any position and in "unlimited" amount;
	- while ranges and frames still must be ordered (there's no built-in sorting ATM), they may be separated into two distinct blocks of extended overrides file.  this is a pleasant side-effect caused by the fact that single frames do not affect framerate and thus can be treated as a mere instructions to EDL generator.
3. run first AvsP macro `tivtcex-phase-3-*.py` to generate TDecimate overrides out of extended overrides:
	- TIVTC works on per-cycle basis and treats video as if it begins from complete telecine pattern, which is not always the case, thus non-mod5 ranges may be trimmed at beginning and end;
	- due to automatic adjustment of boundaries of ranges to be mod5, it's possible that some ranges will collide.  this will break overrides only when different groups of specifiers will be used: `v/vc/i/ii/e/o` VS `f/fc`.  since it is physically impossible to guess what user wanted in each case, and automation of this won't be of much help, I decided that the best solution is to add comments at the end of colliding overrides.  seems like TDecimate discards them, so it should be OK;
	- ranges must begin with numbers ending with a digit 0 or 5, and end with numbers ending with digit 4 or 9, so it shouldn't be too hard/confusing to adjust them;
	- tl;dr: adjust generated overrides when you see a comment at the end of line saying that there is a collision.
4. load AviSynth script `tivtcex-phase-4-*.avs` with TDecimate set up for second pass, but also:
	1. use `orgOut` argument to set path to a file with list of original frame SIDs used in decimated timeline;
	2. set `tcvf1 = False`;
	3. close AviSynth script after a ~10 seconds after the clip have been generated.  this is needed because sometimes TIVTC does not generate `orgOut` file if you close AviSynth script immediately.  probably some bug;
5. run second AvsP macro `tivtcex-phase-5-*.py` to generate EDL and new timestamps;
6. create AviSynth script as shown in `tivtcex-phase-6-clip.avs` with TDecimate replaced by EDL:
	- EDL() supports only planar YUV color spaces;
	- EDL() supports only field-based clips.  support for frame-based clips is in TODO list;
	- all clips must be in same color space (YV12, YV16, etc.);
	- clips for all specifiers must be supplied to EDL, even if you don't use some of them;
	- you can use "dummies" instead of clips with actual processing.  clips for these specifiers may be used interchangeably: v/vc/f/fc/i/e/o, or you can use BlankClip(field_matched).  we need special clip only for bob-deinterlacing because it must have twice as much frames as the `v/vc/f/fc/i/e/o`, but once again, you can use `BlankClip(field_matched, field_matched.Framecount() * 2)`.
	- don't be afraid of performance issues as clips not referenced in EDL will be used only once, during init, to check if all clips have similar properties (picture related stuff).


## how to install and work with AvsP macros
1. copy included Python scripts into AvsP `AvsP\macros` folder;
2. restart AvsP;
3. go to Main menu > Macros > {filename_of_installed_macro}.


## notes
it would have been possible to translate TFM metrics to EDL config, but that's only if you won't need it before passing to EDL (e.g., decombing).

steps 3--7 could've been compressed to a single, final step, in form of AvsP macro, but only if there were Python code to calculate list of frames to be decimated out of TDecimate metrics.  if this were true, TFM and TDecimate could've been replaced by a more generic filter chain and AvsP macros.

steps 3--7 also can be embedded into TIVTC itself, though this will mean that TIVTC will rely on 3rd-party plugin, which is a bad design.  it is possible to merge EDL code into TIVTC, but once again it's something better not to be done.  ideally TIVTC should be refactored into "analyzer" and "processor": "analyzer" will collect field-matching *and* decimation stats, and "processor" will be a standalone CLI software that will interpret those stats and generate EDL.

we must use timecodes generated by TDecimate because of weird 17.98 FPS as I didn't look at what causes it/how to translate that logic into Python code, esp. considering that arguably it's the very core of TIVTC.  VIVTC, VapourSynth analogue, has a much smaller code base (~1.5 kLoC vs ~5.5 kLoC, among which ~500 LoC are VDecimate code), so it may help with this task.

lines in extended overrides adhere to this structure (pseudo BNF):
```
line ::= ( ( range set_of_range_specifiers ) | ( frame set_of_frame_specifiers offset? ) )? comment?
range ::= integer comma integer
set_of_range_specifiers ::= "v" | "vc" | "f" | "fc" | "ii" | "i" | "e" | "o"
frame ::= integer
set_of_frame_specifiers ::= "v" | "vc" | "f" | "fc" | "i" | "e" | "o"
offset ::= ( "+" | "-" ) integer
comment ::= "#" any_symbol?
* tabs/spaces are allowed in any position and in "unlimited" amount.
```

I've read somewhere that you should compile AviSynth plugins with __stdcall, but because I couldn't find the source of this info, and because TIVTC 1.0.5 is set to use __cdecl, both DLLs were compiled using default __cdecl.
