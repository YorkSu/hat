"""
  hat.utils.config
"""

# pylint: disable=no-name-in-module
# pylint: disable=import-error
# pylint: disable=wildcard-import
# pylint: disable=unused-argument
# pylint: disable=protected-access
# pylint: disable=bare-except


__all__ = [
  'config'
]


import os

import tensorflow as tf
from tensorflow.python.keras.preprocessing.image import ImageDataGenerator

from hat.utils.importer import importer
from hat.utils.logger import logger
from hat.utils.timer import timer
from hat.dataset import *
from hat.model import *


class config(object):
  """
    config
  """
  def __init__(self, *args, **kwargs):
    # set gpu memory growth
    self.gpus = tf.config.experimental.list_physical_devices('GPU')
    for gpu in self.gpus:
      tf.config.experimental.set_memory_growth(gpu, True)
    
    self.raw_input = input('=>')
    self._default()
    self._envs()
    self._proc_input()
    self._proc_envs()

  # Built-in method

  def _set(self, name, data):
    self.__dict__[name] = data

  def _default(self):
    self.dataset_name = 'mnist'
    self.lib_name = 'standard'
    self.model_name = 'mlp'
    self.batch_size = 128
    self.epochs = 5
    self.opt = 'adam'
    self.loss = 'sparse_categorical_crossentropy'
    self.metrics = ['accuracy']
    self.dtype = 'float32'

    self.aug = ImageDataGenerator(
      rotation_range=10,
      width_shift_range=0.05,
      height_shift_range=0.05,
      shear_range=0.05,
      zoom_range=0.05,
      horizontal_flip=True,
    )

    self.name_map = {
      ## set

      # dataset_name
      'd': {'n': 'dataset_name'},
      'dat': {'n': 'dataset_name'},
      'dataset': {'n': 'dataset_name'},
      # lib_name
      'l': {'n': 'lib_name'},
      'lib': {'n': 'lib_name'},
      # model_name
      'm': {'n': 'model_name'},
      'mod': {'n': 'model_name'},
      'model': {'n': 'model_name'},
      # batch_size
      'b': {'n': 'batch_size', 'l': True},
      'bat': {'n': 'batch_size', 'l': True},
      'batchsize': {'n': 'batch_size', 'l': True},
      # epochs
      'e': {'n': 'epochs', 'l': True},
      'ep': {'n': 'epochs', 'l': True},
      'epochs': {'n': 'epochs', 'l': True},
      # opt
      'o': {'n': 'opt', 'l': True},
      'opt': {'n': 'opt', 'l': True},
      # run_mode
      'r': {'n': 'run_mode'},
      'rm': {'n': 'run_mode'},
      'runmode': {'n': 'run_mode'},
      # addition
      'a': {'n': 'addition', 'force_str': True},
      'add': {'n': 'addition', 'force_str': True},
      'addition': {'n': 'addition', 'force_str': True},

      ## tag

      # gimage
      '-g': {'n': 'run_mode', 'd': 'gimage'},
      'gimage': {'n': 'run_mode', 'd': 'gimage'},
      # no-gimage
      '-ng': {'n': 'run_mode', 'd': 'no-gimage'},
      'no-gimage': {'n': 'run_mode', 'd': 'no-gimage'},
      # train-only
      '-t': {'n': 'run_mode', 'd': 'train'},
      'train-only': {'n': 'run_mode', 'd': 'train'},
      # val-only
      '-v': {'n': 'run_mode', 'd': 'val'},
      'val-only': {'n': 'run_mode', 'd': 'val'},
      # data enhance
      '-e': {'n': 'is_enhance', 'd': True},
      'd-e': {'n': 'is_enhance', 'd': True},
      'data-enhance': {'n': 'is_enhance', 'd': True},
      # xgpu

      # learning rate alterable
      '-l': {'n': 'lr_alt', 'd': True},
      'lr-alt': {'n': 'lr_alt', 'd': True},
      # no-flops
      '-nf': {'n': 'is_flops', 'd': False},
      'no-flops': {'n': 'is_flops', 'd': False},
    }

  def _envs(self):

    self._warning_list = []
    self._input_late_parameters = {}
    self._logc = []

    self.is_train = True
    self.is_val = True
    self.is_save = True
    self.is_gimage = True
    self.is_flops = True
    self.is_enhance = False

    self.xgpu = False
    self.xgpu_num = 0
    self.xgpu_max = len(self.gpus)

    self.run_mode = ''
    self.addition = ''
    self.lr_alt = False

    self.dataset = None
    self.model = None
    self.log = None
    self.timer = None
    self.config = None

    self.log_dir = 'logs'
    self.h5_name = ''
    self.load_name = ''
    self.save_name = ''
    self.save_dir = ''
    self.save_time = 1
    self.tb_dir = ''

    # dataset parameters
    self.mission_list = []
    self.num_train = 0
    self.num_val = 0
    self.num_test = 0
    self.input_shape = ()
    self.output_shape = ()
    self.train_x = None
    self.train_y = None
    self.val_x = None
    self.val_y = None
    self.test_x = None
    self.test_y = None

  def _proc_input(self):
    in_list = self.raw_input.split(' ')
    for i in in_list:

      if i in ['', ' ']:
        continue
      
      if '=' in i:
        temp = i.split('=')
        if temp[0] not in self.name_map:
          self._warning_list.append(f'Unsupported option: {temp[0]}')
          continue
        var = self.name_map[temp[0]]
        if 'd' in var:
          self._warning_list.append(f"Can't assign a tag: {temp[0]}")
          continue
        data = temp[1]
        var_name = var['n']
        var_data = int(data) if type(data) == str and data.isdigit() and 'force_str' not in var else data
        if 'l' in var:
          self._input_late_parameters[var_name] = var_data
        else:
          self.__dict__[var_name] = var_data
        continue

      if i not in self.name_map:
        self._warning_list.append(f'Unsupported option: {i}')
        continue
      var = self.name_map[i]
      self.__dict__[var['n']] = var['d']

  def _proc_envs(self):

    # lib
    _importer = importer(self)
    self.lib_name = _importer.get_fullname(self.lib_name)

    ## xgpu
    # pass

    ## dir
    self.save_dir = os.path.join(
      self.log_dir,
      self.lib_name,
      f"{self.model_name}_{self.dataset_name}"
    )
    self.h5_name = os.path.join(
      self.save_dir,
      'save'
    )
    if not os.path.exists(self.save_dir):
      os.makedirs(self.save_dir)
    while True:
      if os.path.exists(f'{self.h5_name}_{self.save_time}.h5'):
        self.save_time += 1
        continue
      self.save_name = f'{self.h5_name}_{self.save_time}.h5'
      if self.save_time == 1:
        self.load_name = ''
        break
      self.load_name = f'{self.h5_name}_{self.save_time-1}.h5'
    self.tb_dir = os.path.join(
      self.save_dir,
      f'tb_{self.save_time}'
    )

    ## logger
    self.log = logger(log_dir=self.save_dir)
    self.log(self.save_dir, t='Logs dir:')
    self.log(self._warning_list, a='Warning')
    
    ## timer
    self.timer = timer(self.log)
    
    ## dataset
    dataset_caller = _importer.load('d', self.dataset_name)
    dataset_caller(self)
    self.log(self.dataset_name, t='Loaded Dataset:')

    ## model
    self.log(self.lib_name, t='Model Lib:')
    model_caller = _importer.load(self.lib_name, self.model_name)
    self.log(self.model_name, t='Loading Model:')
    model_caller(self)
    # late parameters
    for item in self._input_late_parameters:
      ## NOTE:NTF
      # opt is special
      if item == 'opt': continue
      self.__dict__[item] = self._input_late_parameters[item]
    self.model.compile(
      optimizer=self.opt,
      loss=self.loss,
      metrics=self.metrics,
    )
    self.log(self.model_name, _T='Loaded Model:')

    ## run mode && other info
    if self.run_mode == 'no-gimage':
      self.is_gimage = False
      self.log('Do not get model image.')
    if self.run_mode == 'gimage':
      self.is_train = False
      self.is_val = False
      self.is_save = False
      self.log('Get model image only.')
    if self.run_mode == 'trian':
      self.is_val = False
      self.log('Train only.')
    if self.run_mode == 'val':
      self.is_train = False
      self.is_save = False
      self.log('Val only.')
    if self.run_mode != 'gimage':
      self.log(self.batch_size, t='Batch size:')
      self.log(self.epochs, t='Epochs:')
    if self.is_enhance:
      self.log('Enhance data.')
    if self.xgpu:
      self.log('Muti-GPUs.')
    if self.lr_alt:
      self.log('Learning Rate Alterable.')


# test part
if __name__ == "__main__":
  c = config()
