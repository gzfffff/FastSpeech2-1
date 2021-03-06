import os
import glob
import tqdm
import torch
import argparse
import numpy as np
import hparams as hp
from utils.stft import TacotronSTFT
from utils.util import read_wav_np
from dataset.audio_processing import pitch

def main(args):
    stft = TacotronSTFT(filter_length=hp.n_fft,
                        hop_length=hp.hop_length,
                        win_length=hp.win_length,
                        n_mel_channels=hp.n_mels,
                        sampling_rate=hp.sample_rate,
                        mel_fmin=hp.fmin,
                        mel_fmax=hp.fmax)

    wav_files = glob.glob(os.path.join(args.data_path, '**', '*.wav'), recursive=True)
    mel_path = os.path.join(hp.data_dir, 'mels')
    energy_path = os.path.join(hp.data_dir, 'energy')
    pitch_path = os.path.join(hp.data_dir, 'pitch')
    os.makedirs(mel_path, exist_ok=True)
    os.makedirs(energy_path, exist_ok=True)
    os.makedirs(pitch_path, exist_ok=True)
    for wavpath in tqdm.tqdm(wav_files, desc='preprocess wav to mel'):
        sr, wav = read_wav_np(wavpath)
        p = pitch(wav)  # [T, ] T = Number of frames
        wav = torch.from_numpy(wav).unsqueeze(0)      
        mel, mag = stft.mel_spectrogram(wav) # mel [1, 80, T]  mag [1, num_mag, T]
        mel = mel.squeeze(0) # [num_mel, T]
        mag = mag.squeeze(0) # [num_mag, T]
        e = torch.norm(mag, dim=0) # [T, ]
        p = p[:mel.shape[1]]
        id = os.path.basename(wavpath).split(".")[0]
        np.save('{}/{}.npy'.format(mel_path,id), mel.numpy(), allow_pickle=False)
        np.save('{}/{}.npy'.format(energy_path, id), e.numpy(), allow_pickle=False)
        np.save('{}/{}.npy'.format(pitch_path, id), p, allow_pickle=False)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data_path', type=str, required=True,
                        help="root directory of wav files")
    args = parser.parse_args()

    main(args)