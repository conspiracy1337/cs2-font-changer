"""
CS2 Font Changer - Configuration Files Module
Creates the required .conf and .conf.old template files
"""

from pathlib import Path


def create_configuration_files(setup_dir):
    """Create all required configuration files in the setup directory"""
    setup_dir = Path(setup_dir)
    setup_dir.mkdir(parents=True, exist_ok=True)
    
    # Create fonts.conf
    create_fonts_conf(setup_dir)
    
    # Create fonts.conf.old
    create_fonts_conf_old(setup_dir)
    
    # Create 42-repl-global.conf
    create_42_repl_global_conf(setup_dir)
    
    # Create 42-repl-global.conf.old
    create_42_repl_global_conf_old(setup_dir)
    
    print("Configuration files created successfully in setup directory")


def create_fonts_conf(setup_dir):
    """Create fonts.conf template file"""
    fonts_conf_content = """<?xml version='1.0'?>
<!DOCTYPE fontconfig SYSTEM 'fonts.dtd'>
<fontconfig>

	<!-- Choose an OS Rendering Style.  This will determine B/W, grayscale,
	     or subpixel antialising and slight, full or no hinting and replacements (if set in next option) -->
	<!-- Style should also be set in the infinality-settings.sh file, ususally in /etc/profile.d/ -->

	<!-- Choose one of these options:
		Infinality      - subpixel AA, minimal replacements/tweaks, sans=Arial
		Windows 7       - subpixel AA, sans=Arial
		Windows XP      - subpixel AA, sans=Arial
		Windows 98      - B/W full hinting on TT fonts, grayscale AA for others, sans=Arial
		OSX             - Slight hinting, subpixel AA, sans=Helvetica Neue
		OSX2            - No hinting, subpixel AA, sans=Helvetica Neue
		Linux           - subpixel AA, sans=DejaVu Sans

	=== Recommended Setup ===
	Run ./infctl.sh script located in the current directory to set the style.
	
	# ./infctl.sh setstyle
	
	=== Manual Setup ===
	See the infinality/styles.conf.avail/ directory for all options.  To enable 
	a different style, remove the symlink "conf.d" and link to another style:
	
	# rm conf.d
	# ln -s styles.conf.avail/win7 conf.d
	-->

	<dir prefix="default">../../csgo/panorama/fonts</dir>
	<dir>WINDOWSFONTDIR</dir>
	<dir>~/.fonts</dir>
	<dir>/usr/share/fonts</dir>
	<dir>/usr/local/share/fonts</dir>
	<dir prefix="xdg">fonts</dir>

	<!-- A fontpattern is a font file name, not a font name.  Be aware of filenames across all platforms! -->
	<fontpattern>Arial</fontpattern>
	<fontpattern>.uifont</fontpattern>
	<fontpattern>notosans</fontpattern>
	<fontpattern>notoserif</fontpattern>
	<fontpattern>notomono-regular</fontpattern>
	<fontpattern>FONTNAME</fontpattern>
	<fontpattern>.ttf</fontpattern>
	<fontpattern>FONTFILENAME.ttf</fontpattern>
	
	<cachedir>WINDOWSTEMPDIR_FONTCONFIG_CACHE</cachedir>
	<cachedir>~/.fontconfig</cachedir>

	<!-- Uncomment this to reject all bitmap fonts -->
	<!-- Make sure to run this as root if having problems:  fc-cache -f -->
	<!--
	<selectfont>
		<rejectfont>
			<pattern>
				<patelt name="scalable" >
					<bool>false</bool>
				</patelt>
			</pattern>
		</rejectfont>
	</selectfont>
	-->

	<!-- THESE RULES RELATE TO THE OLD MONODIGIT FONTS, TO BE REMOVED ONCE ALL REFERENCES TO THEM HAVE GONE. -->
	<!-- The Stratum2 Monodigit fonts just supply the monospaced digits -->
	<!-- All other characters should come from ordinary Stratum2 -->
	<match>
		<test name="family">
			<string>Stratum2 Bold Monodigit</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>Stratum2</string>
		</edit>
		<edit name="style" mode="assign" binding="strong">
			<string>Bold</string>
		</edit>
	</match>

	<match>
		<test name="family">
			<string>Stratum2 Regular Monodigit</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>Stratum2</string>
		</edit>
		<edit name="weight" mode="assign" binding="strong">
			<string>Regular</string>
		</edit>
	</match>

	<!-- Stratum2 only contains a subset of the Vietnamese alphabet. -->
	<!-- So when language is set to Vietnamese, replace Stratum with Noto. -->
	<!-- Exceptions are Mono and TF fonts. -->
	<!-- Ensure we pick an Italic/Bold version of Noto where appropriate. -->
	<!-- Adjust size due to the Ascent value for Noto being significantly larger than Stratum. -->
	<!-- Adjust size even smaller for condensed fonts.-->
	<match>
		<test name="lang">
			<string>vi-vn</string>
		</test>
		<test name="family" compare="contains">
			<string>Stratum2</string>
		</test>
		<test qual="all" name="family" compare="not_contains">
			<string>TF</string>
		</test>
		<test qual="all" name="family" compare="not_contains">
			<string>Mono</string>
		</test>
		<test qual="all" name="family" compare="not_contains">
			<string>ForceStratum2</string>
		</test>
		<edit name="weight" mode="assign">
			<if>
				<contains>
					<name>family</name>
					<string>Stratum2 Black</string>
				</contains>
				<int>210</int>
				<name>weight</name>
			</if>
		</edit>
		<edit name="slant" mode="assign">
			<if>
				<contains>
					<name>family</name>
					<string>Italic</string>
				</contains>
				<int>100</int>
				<name>slant</name>
			</if>
		</edit>
		<edit name="pixelsize" mode="assign">
			<if>
				<or>
					<contains>
						<name>family</name>
						<string>Condensed</string>
					</contains>
					<less_eq>
						<name>width</name>
						<int>75</int>
					</less_eq>
				</or>
				<times>
					<name>pixelsize</name>
					<double>0.7</double>
				</times>
				<times>
					<name>pixelsize</name>
					<double>0.9</double>
				</times>
			</if>
		</edit>
		<edit name="family" mode="assign" binding="same">
			<string>notosans</string>
		</edit>
	</match>

	<!-- More Vietnamese... -->
	<!-- In some cases (hud health, ammo, money) we want to force Stratum to be used. -->
	<match>
		<test name="lang">
			<string>vi-vn</string>
		</test>
		<test name="family">
			<string>ForceStratum2</string>
		</test>
		<edit name="family" mode="assign" binding="same">
			<string>Stratum2</string>
		</edit>
	</match>

	<!-- Fallback font sizes. -->
	<!-- If we request Stratum, but end up with Arial, reduce the pixelsize because Arial glyphs are larger than Stratum. -->
	<match target="font">
		<test name="family" target="pattern" compare="contains">
			<string>Stratum2</string>
		</test>
		<test name="family" target="font" compare="contains">
			<string>Arial</string>
		</test>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>0.9</double>
			</times>
		</edit>
	</match>

	<!-- If we request Stratum, but end up with Noto, reduce the pixelsize. -->
	<!-- This fixes alignment issues due to the Ascent value for Noto being significantly larger than Stratum. -->
	<match target="font">
		<test name="family" target="pattern" compare="contains">
			<string>Stratum2</string>
		</test>
		<test name="family" target="font" compare="contains">
			<string>Noto</string>
		</test>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>0.9</double>
			</times>
		</edit>
	</match>

 	<!-- Stratum contains a set of arrow symbols in place of certain greek/mathematical characters - presumably for some historical reason, possibly used by VGUI somewhere?. -->
 	<!-- For panorama these Stratum characters should be ignored and picked up from a fallback font instead. -->
	<!-- Update for new source2 versions of Stratum, exclude all four of the greek characters which are included in the new Stratum fonts (sometimes as arrows, sometimes not). Best to fallback in all cases to Arial. -->
	<match target="scan">
		<test name="family">
			<string>Stratum2</string> <!-- This matches all the source2 Stratum fonts except the mono versions -->
		</test>
		<edit name="charset" mode="assign">
			<minus>
				<name>charset</name>
				<charset>
					<int>0x0394</int> <!-- greek delta -->
					<int>0x03A9</int> <!-- greek omega -->
					<int>0x03BC</int> <!-- greek mu -->
					<int>0x03C0</int> <!-- greek pi -->
					<int>0x2202</int> <!-- partial diff -->
					<int>0x2206</int> <!-- delta -->
					<int>0x220F</int> <!-- product -->
					<int>0x2211</int> <!-- sum -->
					<int>0x221A</int> <!-- square root -->
					<int>0x221E</int> <!-- infinity -->
					<int>0x222B</int> <!-- integral -->
					<int>0x2248</int> <!-- approxequal -->
					<int>0x2260</int> <!-- notequal -->
					<int>0x2264</int> <!-- lessequal -->
					<int>0x2265</int> <!-- greaterequal -->
					<int>0x25CA</int> <!-- lozenge -->
				</charset>
			</minus>
		</edit>
	</match>

	<!-- Ban Type-1 fonts because they render poorly --> 
	<!-- Comment this out to allow all Type 1 fonts -->
	<selectfont> 
		<rejectfont> 
			<pattern> 
				<patelt name="fontformat" > 
					<string>Type 1</string> 
				</patelt> 
			</pattern> 
		</rejectfont> 
	</selectfont> 

	<!-- Globally use embedded bitmaps in fonts like Calibri? -->
	<match target="font" >
		<edit name="embeddedbitmap" mode="assign">
			<bool>false</bool>
		</edit>
	</match>

	<!-- Substitute truetype fonts in place of bitmap ones? -->
	<match target="pattern" >
		<edit name="prefer_outline" mode="assign">
			<bool>true</bool>
		</edit>
	</match>

	<!-- Do font substitutions for the set style? -->
	<!-- NOTE: Custom substitutions in 42-repl-global.conf will still be done -->
	<!-- NOTE: Corrective substitutions will still be done -->
	<match target="pattern" >
		<edit name="do_substitutions" mode="assign">
			<bool>true</bool>
		</edit>
	</match>

	<!-- Make (some) monospace/coding TTF fonts render as bitmaps? -->
	<!-- courier new, andale mono, monaco, etc. -->
	<match target="pattern" >
		<edit name="bitmap_monospace" mode="assign">
			<bool>false</bool>
		</edit>
	</match>

	<!-- Force autohint always -->
	<!-- Useful for debugging and for free software purists -->
	<match target="font">
		<edit name="force_autohint" mode="assign">
			<bool>false</bool>
		</edit>
	</match>

	<!-- Set DPI.  dpi should be set in ~/.Xresources to 96 -->
	<!-- Setting to 72 here makes the px to pt conversions work better (Chrome) -->
	<!-- Some may need to set this to 96 though -->
	<match target="pattern">
		<edit name="dpi" mode="assign">
			<double>96</double>
		</edit>
	</match>
	
	<!-- Use Qt subpixel positioning on autohinted fonts? -->
	<!-- This only applies to Qt and autohinted fonts. Qt determines subpixel positioning based on hintslight vs. hintfull, -->
	<!--   however infinality patches force slight hinting inside freetype, so this essentially just fakes out Qt. -->
	<!-- Should only be set to true if you are not doing any stem alignment or fitting in environment variables -->
	<match target="pattern" >
		<edit name="qt_use_subpixel_positioning" mode="assign">
			<bool>false</bool>
		</edit>
	</match>

	<!-- Run infctl.sh or change the symlink in current directory instead of modifying this -->
	<include>../../../core/panorama/fonts/conf.d</include>
	
	<!-- Custom fonts -->
	<!-- Edit every occurency with your font name (NOT the font file name) -->
	
	<match>
		<test name="family">
			<string>Stratum2</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>FONTNAME</string>
		</edit>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>1</double>
			</times>
		</edit>
	</match>
	
	<match>
		<test name="family">
			<string>Stratum2 Bold</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>FONTNAME</string>
		</edit>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>1</double>
			</times>
		</edit>
	</match>
	
	<match>
		<test name="family">
			<string>Arial</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>FONTNAME</string>
		</edit>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>1</double>
			</times>
		</edit>
	</match>
	
	<match>
		<test name="family">
			<string>Times New Roman</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>FONTNAME</string>
		</edit>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>1</double>
			</times>
		</edit>
	</match>
	
	<match>
		<test name="family">
			<string>Courier New</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>FONTNAME</string>
		</edit>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>1</double>
			</times>
		</edit>
	</match>

	<!-- And here's the thing... -->
	<!-- CSGO devs decided to fallback to "notosans" on characters not supplied with "Stratum2" - the font we're trying to replace -->
	<!-- "notosans" or "Noto" is used i.e. on Vietnamese characters - but also on some labels that should be using "Stratum2" or even Arial -->
	<!-- I can't do much about it right now. If you're Vietnamese or something, just delete this <match> closure. -->
	<!-- Some labels (i.e. icon tooltips in menu) won't be using your custom font -->
	<match>
		<test name="family">
			<string>notosans</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>FONTNAME</string>
		</edit>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>1</double>
			</times>
		</edit>
	</match>
	
	<match>
		<test name="family">
			<string>notoserif</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>FONTNAME</string>
		</edit>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>1</double>
			</times>
		</edit>
	</match>
	
	<match>
		<test name="family">
			<string>notomono-regular</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>FONTNAME</string>
		</edit>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>1</double>
			</times>
		</edit>
	</match>

	<match>
		<test name="family">
			<string>noto</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>FONTNAME</string>
		</edit>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>1</double>
			</times>
		</edit>
	</match>

</fontconfig>
"""
    
    fonts_conf_path = setup_dir / "fonts.conf"
    with open(fonts_conf_path, 'w', encoding='utf-8') as f:
        f.write(fonts_conf_content)


def create_fonts_conf_old(setup_dir):
    """Create fonts.conf.old template file (original backup)"""
    fonts_conf_old_content = """<?xml version='1.0'?>
<!DOCTYPE fontconfig SYSTEM 'fonts.dtd'>
<fontconfig>

	<!-- Choose an OS Rendering Style.  This will determine B/W, grayscale,
	     or subpixel antialising and slight, full or no hinting and replacements (if set in next option) -->
	<!-- Style should also be set in the infinality-settings.sh file, ususally in /etc/profile.d/ -->

	<!-- Choose one of these options:
		Infinality      - subpixel AA, minimal replacements/tweaks, sans=Arial
		Windows 7       - subpixel AA, sans=Arial
		Windows XP      - subpixel AA, sans=Arial
		Windows 98      - B/W full hinting on TT fonts, grayscale AA for others, sans=Arial
		OSX             - Slight hinting, subpixel AA, sans=Helvetica Neue
		OSX2            - No hinting, subpixel AA, sans=Helvetica Neue
		Linux           - subpixel AA, sans=DejaVu Sans

	=== Recommended Setup ===
	Run ./infctl.sh script located in the current directory to set the style.
	
	# ./infctl.sh setstyle
	
	=== Manual Setup ===
	See the infinality/styles.conf.avail/ directory for all options.  To enable 
	a different style, remove the symlink "conf.d" and link to another style:
	
	# rm conf.d
	# ln -s styles.conf.avail/win7 conf.d
	-->

	<dir prefix="default">../../csgo/panorama/fonts</dir>
	<dir>WINDOWSFONTDIR</dir>
	<dir>~/.fonts</dir>
	<dir>/usr/share/fonts</dir>
	<dir>/usr/local/share/fonts</dir>
	<dir prefix="xdg">fonts</dir>

	<!-- A fontpattern is a font file name, not a font name.  Be aware of filenames across all platforms! -->
	<fontpattern>Arial</fontpattern>
	<fontpattern>.uifont</fontpattern>
	<fontpattern>notosans</fontpattern>
	<fontpattern>notoserif</fontpattern>
	<fontpattern>notomono-regular</fontpattern>
	
	<cachedir>WINDOWSTEMPDIR_FONTCONFIG_CACHE</cachedir>
	<cachedir>~/.fontconfig</cachedir>

	<!-- Uncomment this to reject all bitmap fonts -->
	<!-- Make sure to run this as root if having problems:  fc-cache -f -->
	<!--
	<selectfont>
		<rejectfont>
			<pattern>
				<patelt name="scalable" >
					<bool>false</bool>
				</patelt>
			</pattern>
		</rejectfont>
	</selectfont>
	-->

	<!-- THESE RULES RELATE TO THE OLD MONODIGIT FONTS, TO BE REMOVED ONCE ALL REFERENCES TO THEM HAVE GONE. -->
	<!-- The Stratum2 Monodigit fonts just supply the monospaced digits -->
	<!-- All other characters should come from ordinary Stratum2 -->
	<match>
		<test name="family">
			<string>Stratum2 Bold Monodigit</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>Stratum2</string>
		</edit>
		<edit name="style" mode="assign" binding="strong">
			<string>Bold</string>
		</edit>
	</match>

	<match>
		<test name="family">
			<string>Stratum2 Regular Monodigit</string>
		</test>
		<edit name="family" mode="append" binding="strong">
			<string>Stratum2</string>
		</edit>
		<edit name="weight" mode="assign" binding="strong">
			<string>Regular</string>
		</edit>
	</match>

	<!-- Stratum2 only contains a subset of the Vietnamese alphabet. -->
	<!-- So when language is set to Vietnamese, replace Stratum with Noto. -->
	<!-- Exceptions are Mono and TF fonts. -->
	<!-- Ensure we pick an Italic/Bold version of Noto where appropriate. -->
	<!-- Adjust size due to the Ascent value for Noto being significantly larger than Stratum. -->
	<!-- Adjust size even smaller for condensed fonts.-->
	<match>
		<test name="lang">
			<string>vi-vn</string>
		</test>
		<test name="family" compare="contains">
			<string>Stratum2</string>
		</test>
		<test qual="all" name="family" compare="not_contains">
			<string>TF</string>
		</test>
		<test qual="all" name="family" compare="not_contains">
			<string>Mono</string>
		</test>
		<test qual="all" name="family" compare="not_contains">
			<string>ForceStratum2</string>
		</test>
		<edit name="weight" mode="assign">
			<if>
				<contains>
					<name>family</name>
					<string>Stratum2 Black</string>
				</contains>
				<int>210</int>
				<name>weight</name>
			</if>
		</edit>
		<edit name="slant" mode="assign">
			<if>
				<contains>
					<name>family</name>
					<string>Italic</string>
				</contains>
				<int>100</int>
				<name>slant</name>
			</if>
		</edit>
		<edit name="pixelsize" mode="assign">
			<if>
				<or>
					<contains>
						<name>family</name>
						<string>Condensed</string>
					</contains>
					<less_eq>
						<name>width</name>
						<int>75</int>
					</less_eq>
				</or>
				<times>
					<name>pixelsize</name>
					<double>0.7</double>
				</times>
				<times>
					<name>pixelsize</name>
					<double>0.9</double>
				</times>
			</if>
		</edit>
		<edit name="family" mode="assign" binding="same">
			<string>notosans</string>
		</edit>
	</match>

	<!-- More Vietnamese... -->
	<!-- In some cases (hud health, ammo, money) we want to force Stratum to be used. -->
	<match>
		<test name="lang">
			<string>vi-vn</string>
		</test>
		<test name="family">
			<string>ForceStratum2</string>
		</test>
		<edit name="family" mode="assign" binding="same">
			<string>Stratum2</string>
		</edit>
	</match>

	<!-- For Japanese prefer Noto Sans JP to Noto Sans SC. -->
	<match>
		<test name="lang">
			<string>ja-jp</string>
		</test>
		<test name="family" compare="contains">
			<string>notosans</string>
		</test>
		<edit name="family" mode="prepend" binding="same">
			<string>notosansJP</string>
		</edit>
	</match>

	<!-- For Japanese default to Noto Sans JP instead of Noto Sans SC when Stratum2 is requested. -->
	<match>
		<test name="lang">
			<string>ja-jp</string>
		</test>
		<test name="family" compare="contains">
			<string>Stratum2</string>
		</test>
		<edit name="family" mode="append_last" binding="same">
			<string>notosansJP</string>
		</edit>
	</match>

	<!-- Fallback font sizes. -->
	<!-- If we request Stratum, but end up with Arial, reduce the pixelsize because Arial glyphs are larger than Stratum. -->
	<match target="font">
		<test name="family" target="pattern" compare="contains">
			<string>Stratum2</string>
		</test>
		<test name="family" target="font" compare="contains">
			<string>Arial</string>
		</test>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>0.9</double>
			</times>
		</edit>
	</match>

	<!-- If we request Stratum, but end up with Noto, reduce the pixelsize. -->
	<!-- This fixes alignment issues due to the Ascent value for Noto being significantly larger than Stratum. -->
	<match target="font">
		<test name="family" target="pattern" compare="contains">
			<string>Stratum2</string>
		</test>
		<test name="family" target="font" compare="contains">
			<string>Noto</string>
		</test>
		<edit name="pixelsize" mode="assign">
			<times>
				<name>pixelsize</name>
				<double>0.9</double>
			</times>
		</edit>
	</match>

 	<!-- Stratum contains a set of arrow symbols in place of certain greek/mathematical characters - presumably for some historical reason, possibly used by VGUI somewhere?. -->
 	<!-- For panorama these Stratum characters should be ignored and picked up from a fallback font instead. -->
	<!-- The latest versions of some of the Stratum fonts have been updated to include greek characaters, so for these we only need to exclude the problem mathematical characters. -->
	<match target="scan">
		<test name="family">
			<string>Stratum2</string> <!-- This matches all the source2 Stratum fonts except the mono versions -->
		</test>
		<edit name="charset" mode="assign">
			<if>									<!-- if font name contains "TF", --> 
				<or>
					<contains>
						<name>fullname</name>
						<string>TF</string>
					</contains>
					<eq>							<!-- or is italic, --> 
						<name>slant</name>
						<int>100</int>
					</eq>
				</or>
				<minus>								<!-- then exclude all problem greek and mathematical characters, -->
					<name>charset</name>
					<charset>
						<int>0x0394</int> <!-- greek delta -->
						<int>0x03A9</int> <!-- greek omega -->
						<int>0x03BC</int> <!-- greek mu -->
						<int>0x03C0</int> <!-- greek pi -->
						<int>0x2202</int> <!-- partial diff -->
						<int>0x2206</int> <!-- delta -->
						<int>0x220F</int> <!-- product -->
						<int>0x2211</int> <!-- sum -->
						<int>0x221A</int> <!-- square root -->
						<int>0x221E</int> <!-- infinity -->
						<int>0x222B</int> <!-- integral -->
						<int>0x2248</int> <!-- approxequal -->
						<int>0x2260</int> <!-- notequal -->
						<int>0x2264</int> <!-- lessequal -->
						<int>0x2265</int> <!-- greaterequal -->
						<int>0x25CA</int> <!-- lozenge -->
					</charset>
				</minus>
				<minus>								<!-- otherwise only exclude the problem mathematical characters. -->
					<name>charset</name>
					<charset>
						<int>0x2202</int> <!-- partial diff -->
						<int>0x2206</int> <!-- delta -->
						<int>0x220F</int> <!-- product -->
						<int>0x2211</int> <!-- sum -->
						<int>0x221A</int> <!-- square root -->
						<int>0x221E</int> <!-- infinity -->
						<int>0x222B</int> <!-- integral -->
						<int>0x2248</int> <!-- approxequal -->
						<int>0x2260</int> <!-- notequal -->
						<int>0x2264</int> <!-- lessequal -->
						<int>0x2265</int> <!-- greaterequal -->
						<int>0x25CA</int> <!-- lozenge -->
					</charset>
				</minus>
			</if>
		</edit>
	</match>

	<!-- Ban Type-1 fonts because they render poorly --> 
	<!-- Comment this out to allow all Type 1 fonts -->
	<selectfont> 
		<rejectfont> 
			<pattern> 
				<patelt name="fontformat" > 
					<string>Type 1</string> 
				</patelt> 
			</pattern> 
		</rejectfont> 
	</selectfont> 

	<!-- Globally use embedded bitmaps in fonts like Calibri? -->
	<match target="font" >
		<edit name="embeddedbitmap" mode="assign">
			<bool>false</bool>
		</edit>
	</match>

	<!-- Substitute truetype fonts in place of bitmap ones? -->
	<match target="pattern" >
		<edit name="prefer_outline" mode="assign">
			<bool>true</bool>
		</edit>
	</match>

	<!-- Do font substitutions for the set style? -->
	<!-- NOTE: Custom substitutions in 42-repl-global.conf will still be done -->
	<!-- NOTE: Corrective substitutions will still be done -->
	<match target="pattern" >
		<edit name="do_substitutions" mode="assign">
			<bool>true</bool>
		</edit>
	</match>

	<!-- Make (some) monospace/coding TTF fonts render as bitmaps? -->
	<!-- courier new, andale mono, monaco, etc. -->
	<match target="pattern" >
		<edit name="bitmap_monospace" mode="assign">
			<bool>false</bool>
		</edit>
	</match>

	<!-- Force autohint always -->
	<!-- Useful for debugging and for free software purists -->
	<match target="font">
		<edit name="force_autohint" mode="assign">
			<bool>false</bool>
		</edit>
	</match>

	<!-- Set DPI.  dpi should be set in ~/.Xresources to 96 -->
	<!-- Setting to 72 here makes the px to pt conversions work better (Chrome) -->
	<!-- Some may need to set this to 96 though -->
	<match target="pattern">
		<edit name="dpi" mode="assign">
			<double>96</double>
		</edit>
	</match>
	
	<!-- Use Qt subpixel positioning on autohinted fonts? -->
	<!-- This only applies to Qt and autohinted fonts. Qt determines subpixel positioning based on hintslight vs. hintfull, -->
	<!--   however infinality patches force slight hinting inside freetype, so this essentially just fakes out Qt. -->
	<!-- Should only be set to true if you are not doing any stem alignment or fitting in environment variables -->
	<match target="pattern" >
		<edit name="qt_use_subpixel_positioning" mode="assign">
			<bool>false</bool>
		</edit>
	</match>

	<!-- Run infctl.sh or change the symlink in current directory instead of modifying this -->
	<include>../../../core/panorama/fonts/conf.d</include>

</fontconfig>
"""
    
    fonts_conf_old_path = setup_dir / "fonts.conf.old"
    with open(fonts_conf_old_path, 'w', encoding='utf-8') as f:
        f.write(fonts_conf_old_content)


def create_42_repl_global_conf(setup_dir):
    """Create 42-repl-global.conf template file"""
    repl_global_content = """<?xml version='1.0'?>
<!DOCTYPE fontconfig SYSTEM 'fonts.dtd'>
<fontconfig>

	<!-- ##Style: common -->

	<!-- Global Replacements - Active if set to true above -->
	<!-- Add your own replacements here -->
	<!-- Clone "match" blocks below for each replacement -->
	<match target="font">
		<test name="family">
			<string>Stratum2</string>
		</test>
		<edit name="family" mode="assign">
			<string>FONTNAME</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>Stratum2</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>FONTNAME</string>
		</edit>
	</match>

	<match target="font">
		<test name="family">
			<string>Stratum2 Bold</string>
		</test>
		<edit name="family" mode="assign">
			<string>FONTNAME</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>Stratum2 Bold</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>FONTNAME</string>
		</edit>
	</match>

	<match target="font">
		<test name="family">
			<string>Arial</string>
		</test>
		<edit name="family" mode="assign">
			<string>FONTNAME</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>Arial</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>FONTNAME</string>
		</edit>
	</match>

	<match target="font">
		<test name="family">
			<string>Times New Roman</string>
		</test>
		<edit name="family" mode="assign">
			<string>FONTNAME</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>Times New Roman</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>FONTNAME</string>
		</edit>
	</match>

	<match target="font">
		<test name="family">
			<string>Courier New</string>
		</test>
		<edit name="family" mode="assign">
			<string>FONTNAME</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>Courier New</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>FONTNAME</string>
		</edit>
	</match>

	<match target="font">
		<test name="family">
			<string>notosans</string>
		</test>
		<edit name="family" mode="assign">
			<string>FONTNAME</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>notosans</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>FONTNAME</string>
		</edit>
	</match>

	<match target="font">
		<test name="family">
			<string>notoserif</string>
		</test>
		<edit name="family" mode="assign">
			<string>FONTNAME</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>notoserif</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>FONTNAME</string>
		</edit>
	</match>

	<match target="font">
		<test name="family">
			<string>notomono-regular</string>
		</test>
		<edit name="family" mode="assign">
			<string>FONTNAME</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>notomono-regular</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>FONTNAME</string>
		</edit>
	</match>

	<match target="font">
		<test name="family">
			<string>noto</string>
		</test>
		<edit name="family" mode="assign">
			<string>FONTNAME</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>noto</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>FONTNAME</string>
		</edit>
	</match>
	
</fontconfig>
"""
    
    repl_global_path = setup_dir / "42-repl-global.conf"
    with open(repl_global_path, 'w', encoding='utf-8') as f:
        f.write(repl_global_content)


def create_42_repl_global_conf_old(setup_dir):
    """Create 42-repl-global.conf.old template file (original backup)"""
    repl_global_old_content = """<?xml version='1.0'?>
<!DOCTYPE fontconfig SYSTEM 'fonts.dtd'>
<fontconfig>

	<!-- ##Style: common -->

	<!-- Global Replacements - Active if set to true above -->
	<!-- Add your own replacements here -->
	<!-- Clone "match" blocks below for each replacement -->
	<match target="font">
		<test name="family">
			<string>FONT TO REPLACE 1</string>
		</test>
		<edit name="family" mode="assign">
			<string>REPLACEMENT FONT 1</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>FONT TO REPLACE 1</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>REPLACEMENT FONT 1</string>
		</edit>
	</match>

	<match target="font">
		<test name="family">
			<string>FONT TO REPLACE 2</string>
		</test>
		<edit name="family" mode="assign">
			<string>REPLACEMENT FONT 2</string>
		</edit>
	</match>
	<match target="pattern">
		<test name="family">
			<string>FONT TO REPLACE 2</string>
		</test>
		<edit name="family" mode="prepend" binding="strong">
			<string>REPLACEMENT FONT 2</string>
		</edit>
	</match>
	
</fontconfig>
"""
    
    repl_global_old_path = setup_dir / "42-repl-global.conf.old"
    with open(repl_global_old_path, 'w', encoding='utf-8') as f:
        f.write(repl_global_old_content)


if __name__ == "__main__":
    # Test the file creation
    from PyQt5.QtCore import QStandardPaths
    test_setup_dir = Path(QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)).parent / "cns" / "cs2-font-changer" / "setup"
    create_configuration_files(test_setup_dir)
    print(f"Test files created in: {test_setup_dir}")