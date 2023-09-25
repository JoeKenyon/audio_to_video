import threading
import ffmpeg
import random
import os
import math

fps = 10  # Use 10 fps (the default is 25fps).

# could use cmd line args for this, but its up to you
audio_dir = "/Users/joekenyon/Desktop/python gui test/audio"
image_dir = "/Users/joekenyon/Pictures"
video_dir = "/Users/joekenyon/Desktop/python gui test/video"

# get list of audio files and image files for video conversion
audio_files = [os.path.join(audio_dir, file) for file in os.listdir(audio_dir) if file.endswith(".mp3")]
image_files = [os.path.join(image_dir, file) for file in os.listdir(image_dir) if file.endswith(".jpeg") or file.endswith('.png')]

# generate a ffmpeg command from an audio file and image file
# command should convert the audio to video using a still frame
def generate_command(audio_in, image_in, video_type=".mov"):

    # generate video file name, just audio file name + .mov
    video_file = video_dir+"/" + os.path.split(audio_in)[1] + video_type

    # now we generate the ffmpeg command to convert audio to video
    audio = ffmpeg.input(audio_in).audio
    image = ffmpeg.input(image_in, loop="1", framerate=fps).video
    ffmpeg_command = ffmpeg.output(image, audio, 
                                   video_file, 
                                   shortest=None, 
                                   vcodec="mjpeg", 
                                   pix_fmt='yuvj420p', 
                                   acodec="mp3")

    return ffmpeg_command

# chunk up a list back on the required number of chunks
# use this to sperate commands for various threads
def chunk_based_on_number(lst, chunk_numbers):
    n = math.ceil(len(lst)/chunk_numbers)

    for x in range(0, len(lst), n):
        each_chunk = lst[x: n+x]

        if len(each_chunk) < n:
            each_chunk = each_chunk + [None for y in range(n-len(each_chunk))]
        yield each_chunk

# generate the commands for each audio file, choose a random image from the image folder
commands = [generate_command(file, random.choice(image_files)) for file in audio_files]

# chunk them up for the threads split them evenly amongst the threads we are using
max_no_of_threads = 50
commands_chunked = list(chunk_based_on_number(commands, chunk_numbers=max_no_of_threads))

threads = []

# perfrom the commands using threading
# this should speed things up
for command_chunk in commands_chunked:
    t = threading.Thread(target= lambda chunk: [command.overwrite_output().run() for command in chunk ], args=(command_chunk,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
