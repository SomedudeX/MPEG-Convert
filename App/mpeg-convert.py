#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# -*-  Style guide  -*-
#
# This file uses the following styles for token names
#
#     PascalCase       Class name
#     snake_case       Variable or function/method name
#     _underscore      Variable/function should be used only intenally in
#                      the scope it's declared in (and should not be
#                      modified by the end user)
#
# Because python does not have a reliable way of signalling the end
# of a particular scope, method, or class, any class/method in this 
# file will always terminate in `return` regardless of the return
# type. 
#
# In addition, python's native type hinting is used whenever possible
# in order to catch issues and minimize problems with static analyzers
#
# This file uses 4 spaces for indentation. 


# -*- Customization -*-
#
# The options specified below are presented to you when converting a file. You
# can customize these options to your liking. For more information/documentation
# on how to customize these questions and parameters, head to the following link:
#
# https://github.com/SomedudeX/MPEG-Convert/tree/main?tab=readme-ov-file#customizing


VIDEO_OPTIONS = [

    {
        "type": "choice",
        "title": "Video resolution...",
        "option": "-s",
        "default": 2,
        "choices": [
            ("1280x720", "1280x720"),
            ("1920x1080", "1920x1080"),
            ("2560x1440", "2560x1440"),
            ("3840x2160", "3840x2160"),
        ]
    },
    
    {
        "type": "choice",
        "title": "Video framerate...",
        "option": "-r",
        "default": 1,
        "choices": [
            ("24 fps", "24"),
            ("30 fps", "30"),
            ("48 fps", "48"),
            ("60 fps", "60"),
        ]
    },
    
    {
        "type": "choice",
        "title": "Video codec...",
        "option": "-c:v",
        "default": 2,
        "choices": [
            ("H.264", "libx264"),       # macOS: change 'libx264' to 'h264_videotoolbox'
            ("H.265", "libx265"),       # macOS: change 'libx265' to 'hevc_videotoolbox'
            ("AV1", "libsvtav1"),
            ("VP9", "libvpx-vp9"),
        ]
    },
    
    {
        "type": "choice",
        "title": "Video quality...",
        "option": "-crf",
        "default": 2,
        "choices": [
            ("CRF 18", "18"),
            ("CRF 21", "21"),
            ("CRF 24", "24"),
            ("CRF 32", "32"),
        ]
    }
]

AUDIO_OPTIONS = [

    {
        "type": "choice",
        "title": "Audio codec...",
        "option": "-c:a",
        "default": 2,
        "choices": [
            ("AAC", "aac"),
            ("MP3", "libmp3lame"),
            ("ALAC", "alac"),
            ("FLAC", "flac"),
        ]
    },
    
    {
        "type": "choice",
        "title": "Audio bitrate...",
        "option": "-b:a",
        "default": 2,
        "choices": [
            ("96k", "96k"),
            ("128k", "128k"),
            ("192k", "192k"),
            ("320k", "320k")
        ]
    },
    
    {
        "type": "choice",
        "title": "Audio samplerate...",
        "option": "-ar",
        "default": 2,
        "choices": [
            ("16000hz", "16000"),
            ("44100hz", "44100"),
            ("48000hz", "48000"),
            ("96000hz", "96000")
        ]
    }
]

# The options specified below are the default options that the program will use when 
# you use the '-d' or '--default' flag. 

DEFAULT_OPTIONS = {
    "r": "24",
    "s": "1920x1080",
    "c:v": "libx264",       # macOS: change 'libx264' to 'h264_videotoolbox'
    "c:a": "libmp3lame", 
    "b:a": "192k", 
    "ar": "44100", 
    "crf": "21", 
    "ac": "2"
}
    

import sys
import json
import platform

from os import path
from os import _exit
from os import getcwd
from time import time

try:
    from ffmpeg import FFmpeg, FFmpegError, Progress

    from rich.progress import TaskProgressColumn, TextColumn
    from rich.progress import BarColumn, TimeRemainingColumn
    from rich.progress import Progress as ProgressBar
    from rich.prompt import Prompt, Confirm
    from rich.console import Console
    from rich import traceback
    
except ModuleNotFoundError as e:
    _error = str(e)
    print(f" \033[91m[Fatal] Module missing: {_error.lower()}")
    print(f" - Make sure you install all required modules by using 'pip'")
    print(f" - Make sure you are using the correct version of python\033[0m")
    print(f" [Info] Mpeg-convert.py terminated with exit code -1")
    raise SystemExit(-1)
    
    
HELP_TEXT = (
"Usage: mpeg-convert.py \\[options] <file.in> <file.out>                \n\
                                                                        \n\
Required args:                                                          \n\
    file.in        The path to the file to convert from                 \n\
    file.out       The path to the file to output to                    \n\
                                                                        \n\
Optional args:                                                          \n\
    --version       Prints the version information to the console       \n\
    -h  --help      Prints this help text and exits                     \n\
    -v  --verbose   Outputs all ffmpeg log to the console               \n\
    -d  --default   Use all default options (customizable from script)  \n\
                                                                        \n\
Custom encoders can be listed by 'ffmpeg -codecs'. Additionally, FFmpeg \n\
will automatically detect the file extensions/containers to convert     \n\
to/from; you do not need to specify anything.                           \n\
                                                                        \n\
Head to https://github.com/SomedudeX/MPEG-Convert/blob/main/README.md   \n\
for more documentation on mpeg-convert.py.                                \
"
)

class ProgramVersion():
    """Represents the version of the system version"""
    
    def __init__(
        self,
        _major: int,
        _minor: int,
        _patch: int,
        _notes: str = ""
    ) -> None:
        """Initializes a version object"""
        self.MAJOR = _major
        self.MINOR = _minor
        self.PATCH = _patch
        self.NOTES = _notes


class FatalError(Exception):
    """Represents a fatal error encountered during the execution of the program"""
    
    def __init__(
        self,
        _exit_code: int = 1,
        _msg: str = "An unknown fatal error occured",
        *_notes: str
    ) -> None:
        """Initializes a FatalError object"""
        self.code = _exit_code
        self.msg = "[Fatal] " + _msg
        self.note = ""
        for index, note in enumerate(_notes):
            if index == 0:
                self.note = f"{note}"
                continue
            self.note += f"\n{note}"
        

class OptionsHandler():
    """The OptionsHandler() class asks the user questions on how to transcode the file"""
    
    def __init__(
        self,
        _metadata: dict,
        _audio_stream: int,
        _video_stream: int,
        _filepath_out: str
    ) -> None:
        """Initializes an instance of OptionsHandler()
        
        + Notes - 
            The _metadata is used only for obtaining information regarding
            the audio channels. 
        
        + Args - 
            _metadata: a dictionary representing the metadata from ffprobe
            _audio_stream: the first audio stream
            _video_stream: the first video stream
        """
        self.console = Console(highlight = False)
        self.error_console = Console(style = "red", highlight = False)
        
        self.options = {}
        self.metadata = _metadata
        self.audio_stream = _audio_stream
        self.video_stream = _video_stream
        
        self._output = _filepath_out
        self.replace = "n"
        
    def ask_encode_options(
        self, 
        _default: bool = False
    ) -> dict[str, str]:
        """Asks the user for encoding options
        
        + Notes -
            Tries to conform to the user's request as much as possible, 
            however in the event that an audio/video stream cannot be 
            discovered, the ask...() function automatically aborts. 
            
            This may lead to unexpected issues. 
            
            Additionally, the custom options are an experimental option, 
            meaning that they are not tested well and may lead to issues. 
        
        + Args -
            _default: whether to use the default options
            
        + Returns -
            Dictionary: representing the commands that matches the user's 
            request. The keys of the dictionary corresponds to the option,
            and the values of the dictionary corresponds to the value in 
            ffmpeg. The options are stripped of the dash (-) in front
            
            e.g. { 'c:a': 'libmp3lame' } corresponds to '-c:a libmp3lame' 
        """
        if _default:
            if path.isfile(self._output):
                self.console.print()
                self.replace = Prompt.ask(
                    " -  Replace existing output path",
                    choices = ["y", "n"],
                    default = "n"
                )
                
                if self.replace == "n":
                    self.console.print()
                    self.console.log("[Info] Finished gathering encoding options")
                    self.console.log("[Info] User declined operation, terminating")
                    raise SystemExit(0)
                    
            self.options = DEFAULT_OPTIONS
            return self.options

        self.console.print()
        self.console.print(" -  Encode for...")
        self.console.print("[1] Audio only")
        self.console.print("[2] Video only")
        self.console.print("[3] Video and audio (default)")
        _encode = Prompt.ask(
            " -  Select an option", 
            choices = ["1", "2", "3"], 
            default = "3"
        )

        self.options: dict = {}
        if _encode == "1": 
            self.options = self._ask_audio_options()
            self.options["vn"] = None
        if _encode == "2": 
            self.options = self._ask_video_options()
            self.options["an"] = None
        if _encode == "3": 
            self.options = (self._ask_video_options() | 
                            self._ask_audio_options())
            
        self.console.print()
        self.console.print("[bold] -*- Miscellaneous options -*-")
        
        if path.isfile(self._output):
            self.console.print()
            self.replace = Prompt.ask(
                " -  Replace existing output path",
                choices = ["y", "n"],
                default = "n"
            )
            
            if self.replace == "n":
                self.console.print()
                self.console.log("[Info] Finished gathering encoding options")
                self.console.log("[Info] User declined operation, terminating")
                raise SystemExit(0)
        
        self.console.print()
        _metadata_strip = Prompt.ask(
            " -  Enable file metadata stripping",
            choices = ["y", "n"],
            default = "y"
        )
        
        self.console.print()
        _additional_commands = Prompt.ask(
            " -  Custom options to ffmpeg ('-option value -option2 value...')\n" +
            " -  Use empty field to skip"
        )
        
        if _metadata_strip == "y":
            self.options["map_metadata"] = "-1"
        if _metadata_strip == "n":
            self.options["map_metadata"] = "0"
        
        self.options = self.options | self._parse_custom_command(_additional_commands)
        
        self.console.print()
        return self.options

    def _ask_audio_options(self) -> dict:
        """Asks the user for audio encoding options
        
        + Notes - 
            If no audio streams are discovered, asks the user if
            they would like to proceed. 
            
        + Returns -
            Dictionary: containing the arguments to pass to FFmpeg. 
        """

        _ret: dict = {}
        
        if self.audio_stream == -1:
            self.error_console.print()
            self.error_console.print("[Error] No audio stream detected in metadata! ")
            self.error_console.print(" - This may lead to unexpected issues")
            self.error_console.print(" - You are entering unknown territory")
            _continue = Confirm.ask("[red] - Would you like to continue?")
            if not _continue:
                return _ret
        
        self.console.print()
        self.console.print("[bold] -*- Audio options -*-")
        for _question in AUDIO_OPTIONS:
            _ret = _ret | self._ask_question(_question)
        
        return _ret

    def _ask_video_options(self) -> dict:
        """Asks the user for video encoding options
        
        + Notes - 
            If no video streams are discovered, asks the user if
            they would like to proceed. 
            
        + Returns -
            Dictionary: containing the arguments to pass to FFmpeg. 
        """
        _ret: dict = {}
        
        if self.video_stream == -1:
            self.error_console.print()
            self.error_console.print("[Error] No video stream detected in metadata! ")
            self.error_console.print(" - This may lead to unexpected issues")
            self.error_console.print(" - You are entering unknown territory")
            _continue = Confirm.ask("[red] - Would you like to continue?")
            if not _continue:
                return _ret
                
        self.console.print()
        self.console.print("[bold] -*- Video options -*-")
        for _question in VIDEO_OPTIONS: 
            _ret = _ret | self._ask_question(_question)

        return _ret
        
    def _ask_question(
        self, 
        _question: dict
    ) -> dict:
        """Asks the user a question
        
        + Args -
            Question: a dictionary input of the different properties of the question
            
        + Returns -
            Dictionary: containing the option (key) and the user's input (value)
        """
        _ret: dict = {}
        
        if _question["option"][0] == "-":                     # The python-ffmpeg api inserts a dash (-) symbol 
            _question["option"] = _question["option"][1:]     # for you, so we have to get rid of the dash.
            
        if _question["type"] == "choice":
            _custom_index = len(_question["choices"]) + 0
            _none_index = len(_question["choices"]) + 1
            _total_length = len(_question["choices"]) + 2
            
            self.console.print()
            self.console.print(" - ", _question["title"])
            self._print_choices(
                _question["choices"],
                _question["default"]
            )
            
            _answer_index = Prompt.ask(
                " -  Select an option", 
                choices = [str(i + 1) for i in range(_total_length)], 
                default = str(_question["default"]),
                
            )
            
            _answer_index = int(_answer_index) - 1
            if _answer_index == _none_index:
                self.console.print(" -  Option removed from ffmpeg arguments")
                return _ret
            if _answer_index == _custom_index:
                _ret[_question["option"]] = Prompt.ask(" -  Custom value")
                return _ret
            
            _ret[_question["option"]] = _question["choices"][_answer_index][1]
            return _ret
                
        if _question["type"] == "input":
            self.console.print()
            _answer_index = Prompt.ask(
                " -  " + _question["title"]
            )
            
            _ret[_question["option"]] = _answer_index
            return _ret
            
        return _ret
        
    def _print_choices(
        self, 
        _choices: list[tuple], 
        _default: int
    ) -> None:
        """Prints the choices from a list of tuples
        
        + Args -
            Choices: a list of tuples contiaining the different options to display
            Default: The index to mark as 'default'
        """
        _custom_index = len(_choices) + 1
        _none_index = len(_choices) + 2
        
        for index, value in enumerate(_choices):
            _number = index + 1
            _line = value[0]
            _line = f"[{_number}] {_line}"
            if _default == index + 1:
                _line = _line + " (default)"
            self.console.print(_line)
            
        self.console.print(f"[{_custom_index}] Custom value")
        self.console.print(f"[{_none_index}] Remove option")
        return
        
    @staticmethod
    def _parse_custom_command(_commands: str) -> dict:
        """Parses the optional commands that the user enters into ffmpeg
        
        + Args -
            Commands: a string of commands that the user enters
        
        + Returns -
            Dictionary: a dictionary containing the options (keys) and the user's
            value (values)
            
        + Notes -
            This method is not extensively tested and is not guaranteed to work
            in all scenarios. Exercise caution when using the custom commands
        """
        _ret: dict = {}
        
        if _commands == "":
            return _ret
            
        _commands += " "
        _option: str = ""
        _value: str = ""
        _is_option: bool = True
        _current_str: str = ""
        
        for _ in range(len(_commands)):
            if len(_commands) == 0:
                break
            if _commands[0] == "-":
                _commands = _commands[1:]
                _is_option = True
                continue
            if _commands[0] == " " and _is_option == True:
                _is_option = False
                _option = _current_str
                _commands = _commands[1:]
                _current_str = ""
                _ret[_option] = None
                continue
            if _commands[0] == " " and _is_option == False:
                _is_option = True
                _value = _current_str
                _commands = _commands[1:]
                _current_str = ""
                _ret[_option] = _value
                continue
                
            _current_str += _commands[0]
            _commands = _commands[1:]
            continue
                
        return _ret


class MetadataLogger():
    """The MetadataLogger() class only has static methods and its only 
    purpose is to log metadata. The class is a `static class`, if you're 
    coming from C#
    """
    
    @staticmethod
    def log_metadata(_metadata: dict) -> None:
        """Prints the contents of a metadata dictionary from ffprobe
        
        + Args -
            Metadata: a dictionary representing the however many streams of data 
            from ffprobe
            
        + Returns - 
            None: the function outputs the information of the different streams
            detected onto the console. 
        """
        _metadata = _metadata["streams"]
        Console().log(f"[Info] Start source info: ", highlight = False)
        
        for _stream in _metadata:
            if _stream["codec_type"] == "video":
                MetadataLogger.log_video_metadata(_stream)
            elif _stream["codec_type"] == "audio":
                MetadataLogger.log_audio_metadata(_stream)
            else:
                Console().log(f"- Auxiliary (stream type '{_stream["codec_type"]}')", highlight = False)
                
        Console().log(f"[Info] End source info ", highlight = False)
        return
    
    @staticmethod
    def log_video_metadata(_video_stream: dict) -> None:
        """Logs the video metadata of a stream onto the console
        
        + Args -
            Video_stream: a dictionary representing a video stream provided by 
            ffprobe
        """
        
        # The notorious 'one liners', except 14 times
        try: _idx: str = f"{_video_stream['index']}"
        except: _idx: str = f"N/A"
        try: _col: str = f"{_video_stream['color_space']}"
        except: _col: str = f"N/A"
        try: _fmt: str = f"{_video_stream['codec_long_name']}"
        except: _fmt: str = f"N/A"
        try: _res: str = f"{_video_stream['width']}x{_video_stream['height']}"
        except: _res: str = f"N/A"
        try: _fps: str = f"{MetadataLogger._get_framerate(_video_stream['avg_frame_rate'])}"
        except: _fps: str = f"N/A"
        try: _dur: str = f"{round(float(_video_stream['duration']), 2)}"
        except: _dur: str = f"N/A"
        try: _fra: str = f"{round(float(_fps) * float(_dur), 2)}"
        except: _fra: str = f"N/A"
        
        Console().log(f"- Video (source stream {_idx})", highlight = False)
        Console().log(f"|    Video codec      : {_fmt}", highlight = False)
        Console().log(f"|    Video color      : {_col}", highlight = False)
        Console().log(f"|    Video resolution : {_res}", highlight = False)
        Console().log(f"|    Video framerate  : {_fps}", highlight = False)
        Console().log(f"|    Video length     : {_dur}s", highlight = False)
        Console().log(f"|    Total frames     : {_fra}", highlight = False)
        return
        
    @staticmethod
    def log_audio_metadata(_audio_stream: dict) -> None:
        """Logs the audio metadata of a stream
        
        + Args -
            Audio_stream: a dictionary representing an audio stream provided by 
            ffprobe
        """
        
        # The notorious 'one liners', except 14 times
        try: _idx: str = f"{_audio_stream['index']}"
        except: _idx: str = f"N/A"
        try: _fmt: str = f"{_audio_stream['codec_long_name']}"
        except: _fmt: str = f"N/A"
        try: _prf: str = f"{_audio_stream['profile']}"
        except: _prf: str = f"N/A"
        try: _smp: str = f"{_audio_stream['sample_rate']} Hz"
        except: _smp: str = f"N/A"
        try: _chn: str = f"{_audio_stream['channels']}"
        except: _chn: str = f"N/A"
        try: _lay: str = f"{_audio_stream['channel_layout'].capitalize()}"
        except: _lay: str = f"N/A"
        try: _btr: str = f"{int(_audio_stream['bit_rate']) // 1000} kb/s"
        except: _btr: str = f"N/A"
        
        Console().log(f"- Audio (source stream {_idx})", highlight = False)
        Console().log(f"|    Audio codec      : {_fmt}", highlight = False)
        Console().log(f"|    Audio profile    : {_prf}", highlight = False)
        Console().log(f"|    Audio samplerate : {_smp}", highlight = False)
        Console().log(f"|    Audio channels   : {_chn}", highlight = False)
        Console().log(f"|    Audio layout     : {_lay}", highlight = False)
        Console().log(f"|    Audio bitrate    : {_btr}", highlight = False)
        return
    
    @staticmethod
    def _get_framerate(_fps: str) -> str:     # Static overload for MetadataManager::get_framerate()
        _numerator = ""                       # It is a member of MetadataLogger because python does
        for _ in range(len(_fps)):            # not support function overloading. See get_framerate()
            if _fps[0] != "/":                # method from class MetadataManager for docs
                _numerator += _fps[0]
                _fps = _fps[1:]
                continue
            _fps = _fps[1:]
            break
            
        _denominator = _fps
        
        _numerator = float(_numerator)
        _denominator = float(_denominator)
        return str(round(_numerator / _denominator, 2))


class MetadataManager():
    """The MetadataManager() class represents a media's metadata"""

    def __init__(
        self, 
        _input_path: str, 
        _debug: bool = False
    ) -> None:
        """Initializes an instance of `MediaManager`

        + Args -
            Input_path: the path of the media file that the object will represent
            Debug: whether to use debug mode or not (debug/verbose mode causes
            the program to output ffmpeg's logs in addition to the program's own
            logs)
        """
        self.console = Console(highlight = False)

        self.input_path = _input_path
        self.get_metadata(_debug)
        
        return

    def get_metadata(
        self, 
        _debug: bool = False
    ) -> None:
        """Gets the metadata of the media file that the object is
        currently representing. This method also loads the audio_stream
        and video_stream attributes, which represents the first
        video/audio stream the program encounters

        + Returns - 
            None: instead, fetches the metadata into the class attribute 
            `self.metadata`
        """
        self.console.log("[Info] Probing file properties and metadata with ffprobe")
        _ffprobe = FFmpeg(executable = "ffprobe").input(
                self.input_path,
                print_format = 'json',
                show_streams = None
        )

        @_ffprobe.on("stderr")
        def ffmpeg_out(_Msg: str) -> None:
            if _debug:
                self.console.log(f"[FFprobe] {_Msg}")

        self.metadata: dict = json.loads(_ffprobe.execute())
        
        self.audio_stream = self.get_audio_stream()
        self.video_stream = self.get_video_stream()
        return

    
        
    def get_audio_stream(self) -> int:
        """Gets the index of the first audio stream in self.metadata. If
        multiple streams are present, the first stream is returned, and
        the rest of the streams are ignored
        
        + Returns -
            Integer: representing the channel of the first audio
            stream. If no audio streams are present in the metadata,
            the function returns -1. 
        """
        _ret: int = -1
        for _stream in self.metadata["streams"]:
            if _stream["codec_type"] == "audio":
                self.console.log(f"[Info] Using first audio stream found (stream {_stream["index"]})")
                _ret = _stream["index"]
                break
        
        if _ret == -1:
            self.console.log(f"[yellow][Warning] No audio stream found")
        return _ret
        
    def get_video_stream(self) -> int:
        """Gets the index of the first video stream in self.metadata. If
        multiple streams are present, the first stream is returned, and
        the rest of the streams are ignored
        
        + Returns -
            Integer: representing the channel of the first video
            stream. If no audio streams are present in the metadata,
            the function returns -1. 
        """
        _ret: int = -1
        for _stream in self.metadata["streams"]:
            if _stream["codec_type"] == "video":
                self.console.log(f"[Info] Using first video stream found (stream {_stream["index"]})")
                _ret = _stream["index"]
                break
        
        if _ret == -1:
            self.console.log(f"[yellow][Warning] No video stream found")
        return _ret

    def get_total_secs(self) -> int:
        """Gets the total length (in seconds) of the first video stream

        + Returns -
            Integer: representing the length (in seconds)
        """
        _ret = self.metadata["streams"][self.video_stream]["duration"]
        _ret = float(_ret)
        return int(_ret)

    def get_framerate(self) -> int:
        """Gets the average framerate of the first video stream. Because
        the framerate is stored as a fractionin ffprobe, and some 
        framerates are not whole numbers, this method has to manually parse
        the framerate by doing division in order to get the framerate as a
        floating-point integer

        + Returns -
            Integer: representing the framerate
        """
        _fps: str = self.metadata["streams"][self.video_stream]["avg_frame_rate"]
        
        _numerator = ""
        for _ in range(len(_fps)):
            if _fps[0] != "/":
                _numerator += _fps[0]
                _fps = _fps[1:]
                continue
            _fps = _fps[1:]
            break
            
        _denominator = _fps
        
        _numerator = float(_numerator)
        _denominator = float(_denominator)
        return int(_numerator // _denominator)


class Program():
    """A media file converter using the ffmpeg engine"""

    def __init__(self) -> None:
        """Initializes an instance of `Program` by initializing the console, 
        parsing the command-line arguments, and verifying thatthe installation
        of ffmpeg is discoverable
        """
        self.VERSION = ProgramVersion(1, 2, 0)
        
        self.console = Console(highlight = False)
        self.error_console = Console(style = "red", highlight = False)
        
        self.verbose = False
        self.default = False
        
        if not sys.stdout.isatty():
            self.console.log("[yellow][Warning] Mpeg-convert.py is not outputting to a tty")
            self.console.log("[yellow]- You might be piping the output for debugging")
            self.console.log("[yellow]- Some functionalities will be limited")
        
        try: 
            self.parse_args()
        except Exception as e:
            _error = str(e)
            raise FatalError(
                1,
                f"Program.parse_args() failed: {_error}",
                f"- Mpeg-convert.py usage: mpeg-convert \\[options] <file.in> <file.out>",
                f"- MPEG-convert.py terminating due to inapt command-line arguments"
            )
        
        self.check_ffmpeg()
        return

    def parse_args(self) -> None:
        """Parses the command-line arguments from the user.
        
        + Notes -
            The path to the current working directories will be appended to
            the input and output arguments if they are relative paths. This
            is because the python-ffmpeg module does not operate in relative
            paths. 
        
            Commands can be listed with the option `-h` or `--help`. 
        """
        
        _input = ""
        _output = ""
        _verbose = False
        _default = False
        
        if len(sys.argv) == 1:
            self.print_help()
            raise SystemExit(0)
        
        _is_flag = True
        for index, value in enumerate(sys.argv):
            if index == 0:
                continue
            if value[0] != "-":
                _is_flag = False
            if _is_flag:
                if value == "--version":
                    self.print_version()
                    raise SystemExit(0)
                elif value == "-h" or value == "--help":
                    self.print_help()
                    raise SystemExit(0)
                elif value == "-d" or value == "--default":
                    _default = True
                elif value == "-v" or value == "--verbose":
                    _verbose = True
                elif value == "-dv" or value == "-vd":
                    _default = True
                    _verbose = True
                else:
                    raise Exception(f"unrecognized option '{value}'")
            else: 
                if len(_input) == 0:
                    _input = value
                elif len(_output) == 0:
                    _output = value
                else:
                    raise Exception(f"unexpected trailing argument '{value}'")

        self.input = _input
        self.output = _output
        self.verbose = _verbose
        self.default = _default
        
        if len(_input) == 0:
            raise Exception(f"input file path not specified")
        if len(_output) == 0:
            raise Exception(f"output file path not specified")
        if not path.isfile(_input):
            raise Exception(f"input path '{_input}' is invalid")
            
        if self.verbose: 
            self.console.log(f"[yellow][Warning] Using verbose mode")
        if self.default: 
            self.console.log(f"[yellow][Warning] Using all default options")
        
        self.console.log(
            f"[Info] Received file paths: '{self.input}', '{self.output}'"
        )
        
        _cwd = getcwd()
        _cwd = _cwd + "/"
        if self.input[0] != "/" and self.input[0] != "~":
                self.input = _cwd + self.input
        if self.output[0] != "/" and self.output[0] != "~":
            self.output = _cwd + self.output
            
        self.console.log(f"[Info] Parsed file paths: '{self.input}', '{self.output}'")
            
        return

    def print_version(self):
        """Prints the version information to the console"""
        _program_version: str = f"v{self.VERSION.MAJOR}.{self.VERSION.MINOR}.{self.VERSION.PATCH}-{self.VERSION.NOTES}"
        _python_version: str = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        _platform: str = f"{sys.platform.capitalize()} ({platform.architecture()[0]} {platform.machine()})"
        
        self.console.print(f"Program  : {_program_version}")
        self.console.print(f"Python   : {_python_version}")
        self.console.print(f"Platform : {_platform}")
        
    def print_help(self):
        """Prints the help usage to the console"""
        self.console.print(HELP_TEXT)

    def check_ffmpeg(self):
        """Checks whether FFmpeg is installed and on the system path
        
        + Notes -
            If FFmpeg is not discoverable, function raises SystemExit and terminated
            program. Otherwise, the function executes succesfully
        """
        try:
            self.console.log("[Info] Verifying FFmpeg installation")
            _ffprobe = FFmpeg(executable = "ffprobe").option("h")
            _ffmpeg = FFmpeg(executable = "ffmpeg").option("h")
            _ffprobe.execute()
            _ffmpeg.execute()
        except FileNotFoundError:
            raise FatalError(
                127,
                "Could not detect FFmpeg executable in system path",
                " - Make sure FFmpeg is installed",
                " - Make sure FFmpeg is in $PATH"
            )
            
        return

    def process(self) -> None:
        """Processes the input file for metadata information (such as 
        framerate, length, etc), outputs the metadata onto the console, 
        and asks the user options on how the program (ffmpeg) should 
        transcode the input file
        
        + Notes -
        
        Because the program uses the total number of video frames to
        determine the progress, audio files (which have no video frames)
        will cause the program's progress bar to be indeterminate
        """
        self.media: MetadataManager    = MetadataManager(self.input, self.verbose)
        self.framerate: None | int     = None
        self.total_secs: None | int    = None
        self.total_frame: None | float = None
        
        try:
            self.framerate   = self.media.get_framerate()
            self.total_secs  = self.media.get_total_secs()
            self.total_frame = self.total_secs * self.framerate
        except Exception as e:
            self.error_console.log(f"[yellow][Warning] Failed retrieving total frames")
            self.error_console.log(f"[yellow] - Mpeg-convert.py uses video frames to calculate remaining time")
            self.error_console.log(f"[yellow] - The progress bar will be indeterminate")
            self.error_console.log(f"[yellow] - Perhaps you are converting an audio file?")
            
        # MPEG-Convert has only been tested for a max
        # of 3 streams (video, audio, subtitles)
        if len(self.media.metadata['streams']) > 3:
            self.console.log(f"[yellow][Warning] Multiple video/audio streams detected")
            self.console.log(f" - Mpeg-convert has not been tested for multiple video/audio streams")
            self.console.log(f" - You are entering unknown territory if you proceed! ")
            self.console.log(f" - This could also be a false detection")
        
        MetadataLogger().log_metadata(self.media.metadata)
        
        self.options_handler = OptionsHandler(
            self.media.metadata, 
            self.media.audio_stream, 
            self.media.video_stream,
            self.output
        )
        
        self.options = self.options_handler.ask_encode_options(self.default)
        self.console.log(f"[Info] Finished gathering encoding options")
        return

    def convert(self) -> None:
        """Starts the conversion of the media file using the FFmpeg() 
        class from python-ffmpeg. Uses the options and metadata gathered 
        from Program::process() to display progress and pass other
        relevant information and arguments to the ffmpeg engine
        
        + Notes - 
            See python-ffmpeg documentation for its api usage
        """
        self.instance = (FFmpeg()
            .option(self.options_handler.replace)
            .input(self.input)
            .output(
                self.output,
                self.options
            )
        )

        self.last_frame: int = 0
        self.start_time: float = time()

        with ProgressBar(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(text_format = "[progress.percentage]{task.percentage:>0.1f}% ({task.completed}/{task.total} frames)"),
            TextColumn("eta", style = "cyan"),
            TimeRemainingColumn(elapsed_when_finished = True),
            console = self.console,
            transient = True
        ) as _bar:

            @self.instance.on("progress")
            def update_progress(_progress: Progress) -> None:
                _bar.update(_task, total = self.total_frame)
                _bar.update(_task, advance = _progress.frame - self.last_frame)
                self.last_frame = _progress.frame

            @self.instance.on("start")
            def show_args(_args: list[str]):
                self.console.log(f"[Info] Initiated FFmpeg task with the following command: {_args}")

            @self.instance.on("stderr")
            def ffmpeg_out(_msg: str) -> None:
                if self.verbose:
                    self.console.log(f"[FFmpeg] {_msg}")

            _task = _bar.add_task("[green]Transcoding file...", total = None)
            self.instance.execute()
            
        return

    def run(self) -> None:
        """The entrypoint of the program. Starts the processing and
        conversions, catches errors should they arise.
        """
        
        try:
            self.process()
            self.convert()
        except FFmpegError as _error:
            raise FatalError(
                1,
                "An FFmpeg exeption has occured",
                f" - Error message from FFmpeg: '{_error.message}'",
                f" - Arguments to execute FFmpeg: {_error.arguments}",
                f" - Use the '-v' or '--verbose' option to hear FFmpeg output",
                f" - Common pitfalls: ",
                f"   * Does the output file have an extension?",
                f"   * Does the extension match the codec?",
                f"   * Is the encoder installed on your system?"
            )
            
        except BrokenPipeError:
            _exit(0)    # When using tee to capture stdout
        
        _total_time = round(time() - self.start_time, 2)
        _total_space = self._readable_size(self.output)
        
        self.console.log(f"[green][Info] Succesfully executed mpeg-convert")
        self.console.log(f"- Took {_total_time} seconds")
        self.console.log(f"- Took {_total_space} of space")
        self.console.log(f"- Output file saved to '{self.output}'")
        return
        
    @staticmethod
    def _readable_size(_path: str, _decimal_point = 2) -> str:
        """Calculates the size of a particular file on disk and returns the
        size in a human-readable fashion
        
        + Args - 
            Path: a path to a file to calculate the size
            Decimal_point: the decimal point to truncate the size to
            
        + Returns -
            String: a string of a human-readable size
        """
        size: float = path.getsize(_path)
        
        for i in ["bytes", "kb", "mb", "gb", "tb", "pb"]:
            if size < 1024.0:
                return f"{size:.{_decimal_point}f} {i}"
            size /= 1024.0
            
        return f"{size:.{_decimal_point}f} pb"


if __name__ == "__main__":
    _printer = Console(highlight = False)
    _err_printer = Console(
        style = "red",
        highlight = False
    )
    
    try:
        traceback.install(show_locals = False)
        instance = Program()
        instance.run()
        raise SystemExit(0)
    except FatalError as e:
        _err_printer.log(f"{e.msg}")
        _err_printer.log(f"{e.note}")
        _printer.log(f"[Info] Mpeg-convert.py terminated with exit code {e.code}")
        raise SystemExit(e.code)
    except KeyboardInterrupt:
        try:
            _printer.print()
            _printer.log("[Warning] Mpeg-convert.py received KeyboardInterrupt", style = "yellow")
            _printer.log("[Warning] Force quitting with os._exit()", style = "yellow")
            _exit(0)                # Force terminate all threads
        except BrokenPipeError: 
            _exit(0)                # When using tee to capture stdout
