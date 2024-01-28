## MPEG-Convert
A python tool based on ffmpeg that makes converting between different formats/codecs a whole lot easier for the end-user

This tool is a simple wrapper for the ffmpeg engine to make the conversion between different video/audio formats a little easier for the folks who doesn't want to memorize twenty options to use ffmpeg. This program is not, however, a complete replacement for ffmpeg in any way. For that purpose, you should look look into other software such as Handbrake or DaVinci Resolve. 

Additionally, this tool has been hacked together in a couple of days, meaning that some of the finer details has not been fleshed out or extensively tested -- expect some rough corners during use. This tool also has not been tested or designed for multiple video/audio streams. 


## Installation
* Clone this repository
  ```bash
  git clone https://github.com/SomedudeX/MPEG-Convert
  ```
* Install required `pip` packages
  ```bash
  cd MPEG-convert
  pip3 install -r requirements.txt
  ```
* Launch the script
  ```
  ./App/mpeg-convert.py -h
  ```

If you would like to launch this script from anywhere, you can add it to the path (duh)
> [!NOTE]
> The installation instructions are for systems running Unix-based systems (macOS/Linux), and has not been tested with Windows. 

## Troubleshooting

* Do you have python installed?
* Do you have ffmpeg installed?

* Common pitfalls:
  + Does the output file have an extension?
  + Does the extension match the codec?
    - `HEVC` with `.mp4`  
    - `ALAC` with `.m4a`
  + Is the encoder installed on your system?

## Usage
```
A media file converter using the ffmpeg engine. 

Usage: mpeg-convert [options] <filepath.in> <filepath.out>

Options:
	-h   --help        Shows the help page
	-d   --debug       Enable debug mode to see FFmpeg logs
	     --default	   Use all default settings

Custom encoders can be listed by `ffmpeg -codecs`

Note:
    FFmpeg will automatically detect the file extensions/containers
    to convert to/from; you do not need to specify anything.
```
--
```
Last updated Jan 2023
Not in active development
```
