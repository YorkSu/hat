# -*- coding: utf-8 -*-
"""Graph

  File: 
    /hat/model/custom/layer/graph

  Description: 
    Graph transformation Layers
"""


import tensorflow as tf

from hat.model.custom.util import normalize_tuple


# import setting
__all__ = [
  'ResolutionScaling2D',
  'ResolutionScal2D',
]


class ResolutionScaling2D(tf.keras.layers.Layer):
  """ResolutionScaling2D
  
    Description:
      None
    
    Attributes:
      size: Int or list of 2 Int.
      data_format: Str, default None. `channels_last`(None) or `channels_first`.

    Returns:
      tf.Tensor

    Raises:
      TypeError
      LenError

    Usage:
      None
  """
  def __init__(
      self,
      size: list,
      data_format=None,
      **kwargs):
    super().__init__(trainable=False, **kwargs)
    self.size = normalize_tuple(size, 2)
    self.data_format = data_format or tf.keras.backend.image_data_format()

  def call(self, inputs, **kwargs):
    x = inputs
    
    if self.data_format == 'channel_first':
      _size = tf.keras.backend.int_shape(x)[2:4]
    else:
      _size = tf.keras.backend.int_shape(x)[1:3]
    dh = self.size[0] - _size[0]
    dw = self.size[1] - _size[1]
    nh = abs(dh) // 2
    nw = abs(dw) // 2
    lh = [nh, abs(dh) - nh]
    lw = [nw, abs(dw) - nw]
    
    if dh < 0:
      x = tf.keras.layers.Cropping2D([lh, [0, 0]])(x)
    elif dh > 0:
      x = tf.keras.layers.ZeroPadding2D([lh, [0, 0]])(x)
    if dw < 0:
      x = tf.keras.layers.Cropping2D([[0, 0], lw])(x)
    elif dw > 0:
      x = tf.keras.layers.ZeroPadding2D([[0, 0], lw])(x)

    return x
    
  def get_config(self):
    config = {
      'size': self.size,
      'data_format': self.data_format,
    }
    return dict(list(super().get_config().items()) + list(config.items()))


# Alias
ResolutionScal2D = ResolutionScaling2D


# test part
if __name__ == "__main__":
  x_ = tf.keras.backend.placeholder((None, 8, 8, 16))
  print(ResolutionScaling2D((6, 6))(x_))
  print(ResolutionScaling2D((10, 10))(x_))
  print(ResolutionScaling2D((10, 6))(x_))
  print(ResolutionScaling2D((10, 10)).\
        compute_output_shape((None, 6, 6, 1)))
  