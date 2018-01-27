## Prerequisites
- [AviSynth >=2.5](https://sourceforge.net/projects/avisynth2/), or [AviSynth+](https://github.com/pinterf/AviSynthPlus/releases);
- AvsP or [AvsPmod](https://github.com/AvsPmod/AvsPmod/releases);
- [EDL](https://github.com/8day/avs-edl/releases) plugin for AviSynth;
- TIVTC plugin with version [>=1.0.5.1](https://github.com/8day/avs-tivtc/releases) for AviSynth >=2.5, or [>=1.0.10](https://github.com/pinterf/TIVTC/releases) for AviSynth+;
- "player" of AviSynth scripts. Most likely either [VirtualDub](https://sourceforge.net/projects/virtualdub/?source=directory) or [AVSMeter](https://forum.doom9.org/showthread.php?t=174797).


## Workflow
1. play `tivtcex-phase-1-*.avs` in VirtualDub/AVSMeter to collect metrics for TFM and TDecimate;
2. analyze field-matched clip as shown in `tivtcex-phase-2-*.avs` and create extended overrides:
	- save *ranges of frames* that need special processing using these specifiers:
		- `v`/`f` -- to mark video/film sections;
		- `vc`/`fc` -- to mark combed video/film sections;
		- `i` -- to mark blend-deinterlaced sections;
		- `ii` -- to mark bob-deinterlaced sections;
		- `e` -- to mark sections with extrapolated even fields from src/undecimated clip;
		- `o` -- to mark sections with extrapolated odd fields from src/undecimated clip.
	- save *frames* that need special processing using any of the specifiers used for ranges, excluding `ii`. You can add `±N` to provide offset within specified clip;
	- decimation pattern is not supported and must be inserted manually after TDecimate overrides will be generated;
	- tabs/spaces are allowed in any position and in "unlimited" amount;
	- while ranges and frames still must be ordered (there's no built-in sorting ATM), they may be separated into two distinct blocks in extended overrides file. This is a pleasant side-effect caused by the fact that single frames do not affect framerate and thus can be treated as a mere instructions to EDL generator.
3. run first AvsP macro `tivtcex-phase-3-*.py` to generate TDecimate overrides out of extended overrides:
	- TIVTC works on per-cycle basis and treats video as if it begins from complete telecine pattern, which is not always the case, thus non-mod5 ranges may be trimmed at beginning and end;
	- due to automatic adjustment of boundaries of ranges to be mod5, it's possible that some ranges will collide. This will break overrides only when different groups of [explicitly defined] specifiers follow one after another (this is unlikely, but nonetheless possible): `v/vc/i/ii/e/o` follows `f/fc` and vice versa. Since it is physically impossible to guess user's intentions as to how to adjust boundaries in such cases, it was decided to add comments at the end of colliding overrides so that user adjusted them himself. TDecimate ignores text he doesn't recognize, so this *should* be safe (this was tested in TIVTC 1.0.5.1);
	- ranges must begin with numbers ending with a digit 0 or 5, and end with numbers ending with digit 4 or 9, so it shouldn't be too hard/confusing to adjust them;
	- tl;dr: adjust generated overrides when you see a comment at the end of line saying that there is a collision.
4. load AviSynth script `tivtcex-phase-4-*.avs` with TDecimate set up for second pass, but also:
	1. use `orgOut` argument to set path to a file with list of original frame SIDs used in decimated timeline;
	2. set `tcvf1 = False`;
	3. close AviSynth script ~10 seconds after the clip have been generated. This is needed because sometimes TIVTC does not generate `orgOut` file if you close AviSynth script immediately. Probably some bug;
5. run second AvsP macro `tivtcex-phase-5-*.py` to generate EDL and new timestamps;
6. create AviSynth script as shown in `tivtcex-phase-6-clip.avs` with TDecimate replaced by EDL:
	- EDL() supports only planar YUV color spaces;
	- all clips must be in same color space (YV12, YV16, etc.);
	- EDL() supports only field-based clips. Support for frame-based clips is in TODO list;
	- clips for all specifiers must be supplied to EDL, even if you don't use some of them. Although, if you won't use clips after, say, `bob_deinter`, you may skip them;
	- you may use `BlankClip(field_matched)` as a dummy clip for unused `v/vc/f/fc/i/e/o`. For `ii` you must use `BlankClip(field_matched, field_matched.Framecount() * 2)`.
	- don't be afraid of performance issues as clips not referenced in EDL will be used only once, during init, to check if all clips have similar properties (picture related stuff).


## How to install and work with AvsP macros
1. copy included Python scripts into AvsP `AvsP\macros` folder;
2. restart AvsP;
3. go to Main menu > Macros > {filename_of_installed_macro}.


## Notes
It would have been possible to translate TFM metrics to EDL config, but that's only if you won't need it before passing to EDL (e.g., decombing).

Steps 3--7 could've been compressed to a single, final step, in form of AvsP macro, but only if there were Python code to calculate list of frames to be decimated out of TDecimate metrics. If this were true, TFM and TDecimate could've been replaced by a more generic filter chain and AvsP macros.

Steps 3--7 also can be embedded into TIVTC itself, though this will mean that TIVTC will rely on 3rd-party plugin, which is a bad design. It is possible to merge EDL code into TIVTC, but once again it's something better not to be done. Ideally TIVTC should be refactored into "analyzer" and "processor": "analyzer" will collect field-matching *and* decimation stats, and "processor" will be a standalone CLI software that will interpret those stats and generate EDL.

We must use timecodes generated by TDecimate because of weird 17.98 FPS as I didn't look at what causes it/how to translate that logic into Python code, esp. considering that arguably it's the very core of TIVTC. VIVTC, VapourSynth analogue, has a much smaller code base (~1.5 kLoC vs ~5.5 kLoC, among which ~500 LoC are VDecimate code), so it may help with this task.

Lines in extended overrides conform to this structure (pseudo BNF):
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
