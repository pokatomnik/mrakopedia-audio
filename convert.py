import glob
import os
import torch
import wave
import logging
import traceback
from pydub import AudioSegment

device = torch.device('cpu')
torch.set_num_threads(4)
local_file = 'model.pt'

if not os.path.isfile(local_file):
    torch.hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt',
                                   local_file)  

model = torch.package.PackageImporter(local_file).load_pickle("tts_models", "model")
model.to(device)

sample_rate = 48000
speaker='baya'

def split_to_sentences(input):
    list = []
    raw_sentences = []
    tmp = ''
    for char in input:
        tmp += char
        if char == '.' or char == '?' or char == '!':
            raw_sentences.append(tmp)
            tmp = ''
    for raw_sentence in raw_sentences:
        sentence = raw_sentence.strip(' \t\n\r').replace('…', '...').replace('#', '').replace('##', '')
        if sentence != '':
            list.append(sentence)
    return list


def read_sentences(filename):
    list = []
    with open(filename, 'r', encoding="utf-8") as file:
        data = file.read().split('\n')
        for raw_paragraph in data:
            paragraph = raw_paragraph.strip(' \t\n\r')
            if paragraph == '':
                continue
            sentences = split_to_sentences(paragraph)
            for sentence in sentences:
                list.append(sentence)
    return list

def clean_working_dir():
    for f in glob.glob("./.tmp/*.wav"):
        os.remove(f)

def join_wavs(infiles, outfile):
    data= []
    for infile in infiles:
        w = wave.open(infile, 'rb')
        data.append( [w.getparams(), w.readframes(w.getnframes())] )
        w.close()

    output = wave.open(outfile, 'wb')
    output.setparams(data[0][0])
    for i in range(len(data)):
        output.writeframes(data[i][1])
    output.close()

def convert_from_wav_to_mp3(source_filename, dest_filename):
    AudioSegment.from_file(source_filename).export(dest_filename, format="mp3")

def convert_textfile_to_audio(source, dest):
    sentences = read_sentences(source)
    sentence_files = []

    clean_working_dir()
    for i, sentence in enumerate(sentences):
        try:
            model.save_wav(text=sentence,
                                    speaker=speaker,
                                    sample_rate=sample_rate)
            sentence_filename = '.tmp/' + str(i) + '.wav'
            sentence_files.append(sentence_filename)
            os.rename("test.wav", sentence_filename)
        except Exception as e:
            print("Current sentence: " + sentence)
            logging.error(traceback.format_exc())

    if len(sentence_files) > 0:
        join_wavs(sentence_files, "result.wav")
        convert_from_wav_to_mp3("result.wav", dest)
        os.remove("result.wav")

    clean_working_dir()
