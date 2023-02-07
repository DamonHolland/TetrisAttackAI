import sys
import os.path

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import tensorflow as tf
import numpy as np


class LiteModel:

    @classmethod
    def from_keras_model(cls, model):
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        lite_model = converter.convert()
        return LiteModel(tf.lite.Interpreter(model_content=lite_model))

    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()[0]
        self.output_details = self.interpreter.get_output_details()
        self.input_index = self.input_details["index"]
        self.output_indexes = [output_detail["index"] for output_detail in self.output_details]
        self.input_shape = self.input_details["shape"]
        self.output_shapes = [output_detail["shape"] for output_detail in self.output_details]
        self.input_dtype = self.input_details["dtype"]
        self.output_dtypes = [output_detail["dtype"] for output_detail in self.output_details]

    def predict(self, inp):
        inp = inp.astype(self.input_dtype)
        count = inp.shape[0]
        outs = [np.zeros((count, shape[1]), dtype=dtype) for shape, dtype in zip(self.output_shapes, self.output_dtypes)]
        for i in range(count):
            self.interpreter.set_tensor(self.input_index, inp[i:i + 1])
            self.interpreter.invoke()
            for out, output_index in zip(outs, self.output_indexes):
                out[i] = self.interpreter.get_tensor(output_index)[0]
        return outs

    def predict_single(self, inp):
        inp = np.array([inp], dtype=self.input_dtype)
        self.interpreter.set_tensor(self.input_index, inp)
        self.interpreter.invoke()
        outs = [self.interpreter.get_tensor(output_index) for output_index in self.output_indexes]
        return [out[0] for out in outs]
