#dependencies
#pip install spleeter
#pip install librosa
#pip install pydub

#split audio
import spleeter


#keyframes
import numpy as np
import librosa
#from librosa import audioread
import matplotlib.pyplot as plt
import argparse
import sys
import subprocess
import os
from pathlib import Path
import json
sys.stdout.write("Parsing arguments ...\n")
sys.stdout.flush()

def parse_args():
    desc = "Blah"

    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--file", type=str, help="input audio")
    parser.add_argument("--fps", type=int, help="frames per second")
    parser.add_argument("--musicstart", type=str, help="start of the music in seconds")
    parser.add_argument("--musicend", type=str, help="length of the music in seconds")
    parser.add_argument("--speed", type=float, default='0.4', help="reactive impact of the audio on the animation")
    args = parser.parse_args()
    return args



args=parse_args();

if args.musicstart and not args.musicend:
        subprocess.run(["python", "length.py", "--file", args.file, "--musicstart", args.musicstart])#, "--musicend",args.musicend])
elif args.musicstart and args.musicend:
        subprocess.run(["python", "length.py", "--file", args.file, "--musicstart", args.musicstart, "--musicend",args.musicend])
elif args.musicend and not args.musicstart:
        subprocess.run(["python", "length.py", "--file", args.file, "--musicend",args.musicend])
else:
        print('audio not cropped')
    

#get the length of the audio

file = args.file


def keyframe_maker():
            file = args.file
            c = Path(file)
            filedir = c.stem
            file_path = file
            
            #calculate duration of the wav
            from pydub import AudioSegment
            length_of_file = librosa.get_duration(filename=file_path)
            audio = AudioSegment.from_file(file_path)
            audio.duration_seconds == (len(audio) / 1000.0)
            minutes_duartion = int(audio.duration_seconds // 60)
            minutes_duration = minutes_duartion * 60
            seconds_duration = round(audio.duration_seconds % 60)
            duration = minutes_duration + seconds_duration
            
            #actual keyframe run
            x, sr = librosa.load(file_path)           

            onset_frames = librosa.onset.onset_detect(x, sr=sr, wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
            #print(onset_frames)
            #len(x)            

            onset_frames = librosa.onset.onset_detect(x, sr=sr, wait=1, pre_avg=1, post_avg=1, pre_max=1, post_max=1)
            onset_times = librosa.frames_to_time(onset_frames)            


            	  
            #@markdown Audio compoenent. Step 1: gets array that has time stamps of beats, and magnitudes. Create array whhere index is 
            fps = args.fps #frames per second
            sec_total = duration # total seconds of audio           

            t_lin_step = 1 / fps # the amount time represented by index
            total_lin_step = sec_total * fps 
            t_lin = np.linspace(0, sec_total, num=total_lin_step) # time steps of each frame and weight             

            vals, bin_edgs = np.histogram(onset_times, bins=total_lin_step, range=(0,sec_total))            

            beat_factor_scale = 2.5
            beat_factor_mask = ((vals+.5)/2)*beat_factor_scale
            print(beat_factor_mask)           

            beat_ind = np.argwhere(vals) # indices in terms of frames in vid of where beat occurs
            beat_ind            

            frames_change_pre_beat = 0
            frames_change_post_beat = 100 # there are the amount of buffer frames before and after a beat to let value linear change
            #   If my beat is at 10.    9:(0), 10:(1), 22:(0). So between frames 10-22 they linearly scale. But look to change from linear to -exp 
            post_beat_transition__value = args.speed/2
            beat_transition_value = args.speed
            pre_beat_transition__value = -args.speed         

            key_frame_ind = beat_ind * np.ones((1, 3))

            key_frame_ind[:, 0] -= (frames_change_pre_beat+1)
            key_frame_ind[:, 2] += (frames_change_post_beat)            

            val_test = key_frame_ind.reshape(key_frame_ind.shape[0],3,1)
            key_frame_value = []
            post_beat = 1
            for i in range(len(beat_ind)):
              #print()
              if post_beat < beat_ind[i]:
                post_tup = (post_beat,  post_beat_transition__value)
                key_frame_value.append(post_tup)
                #print(f"{i}  beat_ind[i]: {beat_ind[i]}, post {post_tup}")
              pre = (beat_ind[i] - frames_change_pre_beat - 1)[0]
              if len(key_frame_value) ==0 or len(key_frame_value)!=0 and key_frame_value[-1][0] != pre:
                #print(f"{i}  beat_ind[i]: {beat_ind[i]}, pre {pre, 0}")
                key_frame_value.append((pre, pre_beat_transition__value))
              beat = beat_ind[i][0]
              #print(f"{i}  beat_ind[i]: {beat_ind[i]}, beat {beat, beat_transition_value}")
              key_frame_value.append((beat,  beat_transition_value))
              post_beat = (beat_ind[i] + (frames_change_post_beat))[0]
              
            print(key_frame_value) 
            
         


            string_list = []
            
            for key_frame, val in key_frame_value:
              string = f"{key_frame}:({val}),"
              string_list.append(string)            

            key_frame_string = "".join(string_list)
            key_frame_string
            
            # save file
            with open("audio_keyframes.json", "w") as fp2:
                json.dump(key_frame_string, fp2)
                print("processing of the bpm succeeded and exported to audio_keyframes.json")
            """save_audio_txt = True#@param {type:"boolean"}  
            if save_audio_txt:
              file_name_no_extension, _ = os.path.splitext(file_path)
              p = Path(file_path)
              filenamer = p.stem
              c = Path(file)
              filedir = c.stem
              zero='output/'+filedir +'keyframes/'
              if not os.path.exists(zero):
                os.mkdir(zero)

              #file_name = f'working_dir/file.wav'
              output_name = 'keyframes/single_keyframes.txt'
              #with open(output_name, 'wt') as f:
              #    f.write('\n'.join([f"{key_frame}:({val}),"]))
              textfile = open(output_name, "w")
              for element in key_frame_string:
                textfile.write(element)"""

keyframe_maker()