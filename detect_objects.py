import numpy as np
import pandas as pd
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
from argparse import ArgumentParser
from configparser import ConfigParser

from distutils.version import StrictVersion
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
import time
from object_detection.utils import ops as utils_ops

if StrictVersion(tf.__version__) < StrictVersion('1.12.0'):
  raise ImportError('Please upgrade your TensorFlow installation to v1.12.*.')

from utils import label_map_util
from utils import visualization_utils as vis_util

def load_image_into_numpy_array(image):
  (im_width, im_height) = image.size
  return np.array(image.getdata()).reshape(
      (im_height, im_width, 3)).astype(np.uint8)


def run_inference_for_single_image(image, graph):
  with graph.as_default():
    with tf.Session() as sess:
      # Get handles to input and output tensors
      ops = tf.get_default_graph().get_operations()
      all_tensor_names = {output.name for op in ops for output in op.outputs}
      tensor_dict = {}
      for key in [
          'num_detections', 'detection_boxes', 'detection_scores',
          'detection_classes', 'detection_masks'
      ]:
        tensor_name = key + ':0'
        if tensor_name in all_tensor_names:
          tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
              tensor_name)
      if 'detection_masks' in tensor_dict:
        # The following processing is only for single image
        detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
        detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
        # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
        real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
        detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
        detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            detection_masks, detection_boxes, image.shape[1], image.shape[2])
        detection_masks_reframed = tf.cast(
            tf.greater(detection_masks_reframed, 0.5), tf.uint8)
        # Follow the convention by adding back the batch dimension
        tensor_dict['detection_masks'] = tf.expand_dims(
            detection_masks_reframed, 0)
      image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

      # Run inference
      output_dict = sess.run(tensor_dict,
                             feed_dict={image_tensor: image})

      # all outputs are float32 numpy arrays, so convert types as appropriate
      output_dict['num_detections'] = int(output_dict['num_detections'][0])
      output_dict['detection_classes'] = output_dict[
          'detection_classes'][0].astype(np.uint8)
      output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
      output_dict['detection_scores'] = output_dict['detection_scores'][0]
      if 'detection_masks' in output_dict:
        output_dict['detection_masks'] = output_dict['detection_masks'][0]
  return output_dict


def get_detections(image_name, image, boxes, classes, scores, cat_index, min_score_thresh=.5):
    im_width, im_height = image.size
    detections = []
    for i in range(boxes.shape[0]):
        if scores is None or scores[i] > min_score_thresh:
            box = tuple(boxes[i].tolist())
            ymin, xmin, ymax, xmax = box
            (left, right, top, bottom) = (xmin * im_width,
                                          xmax * im_width,
                                          ymin * im_height,
                                          ymax * im_height)
            if classes[i] in cat_index.keys():
                class_name = cat_index[classes[i]]['name']
            else:
                class_name='N/A'
            detections.append(
                {'image_id': image_name,
                 'object': class_name,
                 'coordinates': {
                     'left': left,
                     'right': right,
                     'bottom': bottom,
                     'top': top
                 },
                 'score': scores[i]
                 }
            )
    return detections


if __name__ == '__main__':
    # ======= ARGUMENTS from command line=========
    parser = ArgumentParser(description="Arguments for Object Detection")
    parser.add_argument('conf_filepath')
    args = parser.parse_args()

    # read parameters from the configuration file given
    conf_parser = ConfigParser()
    conf_parser.read(args.conf_filepath)
    try:
        input_folder = conf_parser['parameters']['input_folder']
        output_folder = conf_parser['parameters']['output_folder']
        model_folder = conf_parser['parameters']['model_folder']
        labels_path = conf_parser['parameters']['labels_path']
        threshold = float(conf_parser['parameters']['threshold'])
    except KeyError as error:
        print('Please include a [parameters] section with keys: "input_folder", "output_folder", "model_folder",'
              '"labels_path", "threshold" (this should be a number) in your configuration file.')
    # ===== MODEL =====
    # What model to download.
    MODEL_NAME = model_folder 
    MODEL_FILE = MODEL_NAME + '.tar.gz'
    DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

    # Path to frozen detection graph. This is the actual model that is used for the object detection.
    PATH_TO_FROZEN_GRAPH = MODEL_NAME + '/frozen_inference_graph.pb'

    # List of the strings that is used to add correct label for each box.
    # PATH_TO_LABELS = os.path.join('C:/Users/cbb10g/Documents/object-detection/models-master/research/object_detection/data', 'mscoco_label_map.pbtxt')
    PATH_TO_LABELS = labels_path
    # Path where the saved images are saved
    PATH_TO_SAVE_IMAGES_DIR = output_folder
    # download the model
    # opener = urllib.request.URLopener()
    # opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
    # tar_file = tarfile.open(MODEL_FILE)
    # for file in tar_file.getmembers():
    #   file_name = os.path.basename(file.name)
    #   if 'frozen_inference_graph.pb' in file_name:
    #     tar_file.extract(file, os.getcwd())

    # load the model into memory
    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.GraphDef()
      with tf.gfile.GFile(PATH_TO_FROZEN_GRAPH, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

    # loading label map
    category_index = label_map_util.create_category_index_from_labelmap(PATH_TO_LABELS, use_display_name=True)

    # ===== DETECTION =====
    # If you want to test the code with your images, just add path to the images to the TEST_IMAGE_PATHS.
    PATH_TO_TEST_IMAGES_DIR = input_folder
    TEST_IMAGE_PATHS = [PATH_TO_TEST_IMAGES_DIR + '/' + f for f in os.listdir(PATH_TO_TEST_IMAGES_DIR)]
    print(TEST_IMAGE_PATHS)
    # Size, in inches, of the output images.
    IMAGE_SIZE = (12, 8)

    overall_detections = []
    for image_path in TEST_IMAGE_PATHS:
        start_time = time.time()
        image = Image.open(image_path)
        # the array based representation of the image will be used later in order to prepare the
        # result image with boxes and labels on it.
        image_np = load_image_into_numpy_array(image)
        # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
        image_np_expanded = np.expand_dims(image_np, axis=0)
        # Actual detection.
        output_dict = run_inference_for_single_image(image_np_expanded, detection_graph)
        # Visualization of the results of a detection.
        vis_util.visualize_boxes_and_labels_on_image_array(
            image_np,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            category_index,
            instance_masks=output_dict.get('detection_masks'),
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=threshold
        )
        plt.figure(figsize=IMAGE_SIZE)
        # plt.imshow(image_np)
        im_save = Image.fromarray(image_np)
        image_name = os.path.basename(image_path)
        im_save.save(PATH_TO_SAVE_IMAGES_DIR + '/' + image_name)
        end_time = time.time()

        detections = get_detections(image_name,
                                    image,
                                    output_dict['detection_boxes'],
                                    output_dict['detection_classes'],
                                    output_dict['detection_scores'],
                                    category_index,
                                    threshold)
        overall_detections.extend(detections)
        print(detections)
        diff = end_time-start_time
        print(diff // 60, diff % 60)
    pd.DataFrame(overall_detections).to_csv(PATH_TO_SAVE_IMAGES_DIR + '/detections.csv')
