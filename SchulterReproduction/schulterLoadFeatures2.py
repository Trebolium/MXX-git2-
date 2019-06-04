try:
    from code.schultercore3 import *
except ImportError:
    from schultercore3 import *   # when running from terminal, the directory may not be identified as a packagefrom keras.callbacks import ModelCheckpoint
# schultercore.py has additional functions
import os, shutil, librosa
import numpy as np
import time
import matplotlib.pyplot as plt

import csv
import math

params=load_parameters()

print('gathering files...')
train_dir = 'jamendo/audioTrain/'
train_files = [train_dir + x for x in os.listdir(train_dir) if x.endswith('.wav') or x.endswith('.ogg') or x.endswith('.mp3')]
val_dir = 'jamendo/audioVal/'
val_files = [val_dir + x for x in os.listdir(val_dir) if x.endswith('.wav') or x.endswith('.ogg') or x.endswith('.mp3')]
test_dir = 'jamendo/audioTest/'
test_files = [test_dir + x for x in os.listdir(test_dir) if x.endswith('.wav') or x.endswith('.ogg') or x.endswith('.mp3')]
print(len(train_files), 'train files \n', len(val_files), 'validation files \n', len(test_files), 'test files')
label_dir= 'jamendo/labels/' #soon to be changed to 'jamendo/betterlabels'
label_files = [label_dir + x for x in os.listdir(label_dir) if x.endswith('.lab')]
# for testing only
test_folder_dir= 'jamendo/testFolder/'
test_folder_files = [test_folder_dir + x for x in os.listdir(test_folder_dir) if x.endswith('.wav') or x.endswith('.ogg') or x.endswith('.mp3')]

print('setting up hdf5 file...')

num_train_instances = len(train_files)
num_val_instances = len(val_files)

image_height=params['n_mel']
image_width=int(np.round(params['max_song_length'] * params['fs'] / float(params['hop_length'])))

dataset = h5py.File('jamendo/jdataset.hdf5', mode='w')


# we store one image per instance of size image_height x image_width holding floating point numbers
dataset.create_dataset('train_features',
                       shape=(num_train_instances, image_height, image_width+1),
                       dtype=np.float)
dataset.create_dataset('val_features',
                       shape=(num_val_instances, image_height, image_width+1),
                       dtype=np.float)
# create dataset for length of songs in ms
dataset.create_dataset('train_lengths',
                       shape=(num_train_instances, 1),
                       dtype=np.int)
dataset.create_dataset('val_lengths',
                       shape=(num_val_instances, 1),
                       dtype=np.int)
# create dataset for labellings
  # odd rows for onsets, even rows for offsets
  # saying 500 for assumed maximum annotations
dataset.create_dataset('train_labels',
                       shape=(num_train_instances, 500),
                       dtype=np.float)
dataset.create_dataset('val_labels',
                       shape=(num_val_instances, 500),
                       dtype=np.float)

# TRAIN TRAIN SET
print('working on train set...')

for k, audio_path in enumerate(train_files):
    print('  ', k +1, '/', len(train_files), audio_path)
    # extract the feature
    label_name = os.path.basename(audio_path)[:-4]+'.lab'
    label_points = np.genfromtxt(label_dir+label_name,delimiter=' ')
    label_points=np.asarray(label_points[:,0])
    label_points = np.concatenate((label_points,np.zeros(500-label_points.shape[0])))
    dataset['train_labels'][k, ...] = label_points
    feature, audio_melframe_nums = extract_feature(audio_path, params)
    plot_save_feature('Train',feature, os.path.basename(audio_path))
    # we can deduce the label from the file name
    dataset['train_features'][k, ...] = feature
    dataset['train_lengths'][k, ...] = audio_melframe_nums

# TRAIN TRAIN SET
print('working on val set...')

for k, audio_path in enumerate(val_files):
    print('  ', k + 1, '/', len(val_files), audio_path)
    # extract the feature
    label_name = os.path.basename(audio_path)[:-4]+'.lab'
    label_points = np.genfromtxt(label_dir +label_name,delimiter=' ')
    label_points=np.asarray(label_points[:,0])
    label_points = np.concatenate((label_points,np.zeros(500-label_points.shape[0])))
    dataset['val_labels'][k, ...] = label_points
    feature, audio_melframe_nums = extract_feature(audio_path, params)
    plot_save_feature('Val',feature, os.path.basename(audio_path))
    # we can deduce the label from the file name
    dataset['val_features'][k, ...] = feature
    dataset['val_lengths'][k, ...] = audio_melframe_nums