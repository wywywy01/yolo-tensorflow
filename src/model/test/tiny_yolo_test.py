# -*- coding: utf8 -*-
# author: ronniecao
from __future__ import print_function
import sys
import os
import time
import numpy
import matplotlib.pyplot as plt
import cv2
import tensorflow as tf
from src.data.image import ImageProcessor
from src.model.tiny_yolo import TinyYolo


class TinyYoloTestor:
    
    def test_iou(self):
            
        label = [[0, 0, 0, 0, 0]] * 5
        label[0] = [0.5, 0.15, 0.8, 0.2, 1]
        label[1] = [0.5, 0.7, 0.1, 0.2, 1]
        label[2] = [0.5, 0.9, 0.6, 0.1, 1]
        
        pred = numpy.zeros(shape=(3,3,2,5))
        pred[1,0,0,:] = [0.5, 0.17, 0.7, 0.25, 1.0]
        pred[1,2,0,:] = [0.5, 0.7, 0.15, 0.25, 1.0]
        pred[1,2,1,:] = [0.5, 0.85, 0.3, 0.15, 1.0]
        class_pred = numpy.zeros(shape=(1, 3, 3, 1))
        
        image_processor = ImageProcessor(
            'Z:', image_size=256, max_objects_per_image=5, cell_size=3, n_classes=1)
        class_label, class_mask, box_label, object_mask, nobject_mask, object_num = \
           image_processor.process_label(label)
            
        tiny_yolo = TinyYolo(
            n_channel=3, n_classes=1, image_size=256, max_objects_per_image=5,
            cell_size=3, box_per_cell=2, object_scala=10, nobject_scala=5,
            coord_scala=10, class_scala=1, batch_size=1)
        
        box_pred = tf.placeholder(
            dtype=tf.float32, shape=[3, 3, 2, 4], name='box_pred')
        box_truth = tf.placeholder(
            dtype=tf.float32, shape=[3, 3, 1, 4], name='box_truth')
        iou_matrix = tiny_yolo.iou(box_pred, box_truth)
        sess = tf.Session()
        [output] = sess.run(
            fetches=[iou_matrix],
            feed_dict={box_pred: pred[:,:,:,0:4], box_truth: box_label[:,:,2:3,0:4]})
        sess.close()
        print(output, output.shape)
        
        # 画图
        image = numpy.zeros(shape=(256, 256, 3), dtype='uint8') + 255
        cv2.line(image, (0, int(256/3.0)), (256, int(256/3.0)), (100, 149, 237), 1)
        cv2.line(image, (0, int(256*2.0/3.0)), (256, int(256*2.0/3.0)), (100, 149, 237), 1)
        cv2.line(image, (int(256/3.0), 0), (int(256/3.0), 256), (100, 149, 237), 1)
        cv2.line(image, (int(256*2.0/3.0), 0), (int(256*2.0/3.0), 256), (100, 149, 237), 1)
        for center_x, center_y, w, h, prob in label:
            if prob != 1.0:
                continue
            # 画中心点
            cv2.circle(image, (int(center_x*256), int(center_y*256)), 2, (255, 99, 71), 0)
            # 画真实框
            xmin = int((center_x - w / 2.0) * 256)
            xmax = int((center_x + w / 2.0) * 256)
            ymin = int((center_y - h / 2.0) * 256)
            ymax = int((center_y + h / 2.0) * 256)
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (255, 99, 71), 0)
        for x in range(3):
            for y in range(3):
                for n in range(2):
                    [center_x, center_y, w, h, prob] = pred[x, y, n, :]
                    # 画中心点
                    cv2.circle(image, (int(center_x*256), int(center_y*256)), 2, (238, 130, 238), 0)
                    # 画预测框
                    xmin = int((center_x - w / 2.0) * 256)
                    xmax = int((center_x + w / 2.0) * 256)
                    ymin = int((center_y - h / 2.0) * 256)
                    ymax = int((center_y + h / 2.0) * 256)
                    cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (238, 130, 238), 0)
            
        plt.imshow(image)
        plt.show()
        
    def test_inference(self):
        tiny_yolo = TinyYolo(
            n_channel=3, n_classes=1, image_size=256, max_objects_per_image=5,
            cell_size=3, box_per_cell=2, object_scala=10, nobject_scala=5,
            coord_scala=10, class_scala=1, batch_size=1)
        
        image = numpy.array(numpy.random.random(size=(1, 256, 256, 3)) * 255, dtype='float32')
        img = tf.placeholder(
            dtype=tf.float32, shape=[1, 256, 256, 3], name='img')
        logits = tiny_yolo.inference(img)
        sess = tf.Session()
        sess.run(tf.global_variables_initializer())
        [output] = sess.run(
            fetches=[logits], 
            feed_dict={img: image})
        sess.close()
        print(output, output.shape)
        
    def test_loss(self):
        label = [[0, 0, 0, 0, 0]] * 5
        label[0] = [0.5, 0.15, 0.8, 0.2, 1]
        label[1] = [0.5, 0.7, 0.1, 0.2, 1]
        label[2] = [0.5, 0.9, 0.6, 0.1, 1]
        
        box_pred = numpy.zeros(shape=(3,3,2,5))
        box_pred[1,0,0,:] = [0.5, 0.17, 0.7, 0.25, 1.0]
        box_pred[1,2,0,:] = [0.5, 0.7, 0.15, 0.25, 1.0]
        box_pred[1,2,1,:] = [0.5, 0.85, 0.3, 0.15, 1.0]
        class_pred = numpy.zeros(shape=(1, 3, 3, 1))
        class_pred[0,0,0] = 1
        class_pred[0,1,0] = 1
        class_pred[0,2,0] = 1
        class_pred[0,1,1] = 1
        class_pred[0,1,2] = 1
        
        pred = numpy.concatenate([class_pred, numpy.reshape(box_pred, (1, 3, 3, 2*5))], axis=3)
        pred = numpy.reshape(pred, (1, 3 * 3 * (1 + 2 * 5)))
        
        image_processor = ImageProcessor(
            'Z:', image_size=256, max_objects_per_image=3, cell_size=3, n_classes=1)
        class_label, class_mask, box_label, object_mask, nobject_mask, object_num = \
           image_processor.process_label(label)
           
        tiny_yolo = TinyYolo(
            n_channel=3, n_classes=1, image_size=256, max_objects_per_image=3,
            cell_size=3, box_per_cell=2, object_scala=1, nobject_scala=1,
            coord_scala=1, class_scala=1, batch_size=1)
        
        image = numpy.array(numpy.random.random(size=(1, 256, 256, 3)) * 255, dtype='float32')
        
        logits = tf.placeholder(
            dtype=tf.float32, shape=[1, 99], name='logits')
        class_loss, coord_loss, object_loss, nobject_loss, \
            iou_value, object_value, nobject_value, recall_value = tiny_yolo.loss(logits)
        
        sess = tf.Session()
        sess.run(tf.global_variables_initializer())
        output = sess.run(
            fetches=[class_loss, object_loss, nobject_loss, coord_loss, 
                     iou_value, object_value, nobject_value, recall_value],
            feed_dict={
                logits: pred,
                tiny_yolo.class_labels: numpy.array([class_label]),
                tiny_yolo.class_masks: numpy.array([class_mask]),
                tiny_yolo.box_labels: numpy.array([box_label]),
                tiny_yolo.object_masks: numpy.array([object_mask])})
        sess.close()
        print(output)
        
    def test_region_layer(self):
        label = [[0, 0, 0, 0, 0]] * 5
        label[0] = [0.25, 0.6, 0.1, 0.2, 1]
        
        box_pred = numpy.zeros(shape=(2,2,1,5))
        box_pred[0,1,0,:] = [0.25, 0.6, 0.05, 0.2, 1.0]
        class_pred = numpy.zeros(shape=(1, 2, 2, 1))
        class_pred[0,0,0] = 1
        class_pred[0,0,1] = 1
        
        pred = numpy.concatenate([class_pred, numpy.reshape(box_pred, (1, 2, 2, 1*5))], axis=3)
        pred = numpy.reshape(pred, (1, 2 * 2 * (1 + 1 * 5)))
        
        
        image_processor = ImageProcessor(
            'Z:', image_size=64, max_objects_per_image=2, cell_size=2, n_classes=1)
        class_label, class_mask, box_label, object_mask, nobject_mask, object_num = \
           image_processor.process_label(label)
           
        tiny_yolo = TinyYolo(
            n_channel=3, n_classes=1, image_size=64, max_objects_per_image=2,
            cell_size=2, box_per_cell=1, object_scala=1, nobject_scala=1,
            coord_scala=1, class_scala=1, batch_size=1)
        
        image = numpy.array(numpy.random.random(size=(1, 64, 64, 3)) * 255, dtype='float32')
        
        logits = tf.placeholder(
            dtype=tf.float32, shape=[1, 24], name='logits')
        class_loss, coord_loss, object_loss, nobject_loss, \
            iou_value, object_value, nobject_value, recall_value = tiny_yolo.loss(logits)
        
        sess = tf.Session()
        sess.run(tf.global_variables_initializer())
        output = sess.run(
            fetches=[class_loss, object_loss, nobject_loss, coord_loss, 
                     iou_value, object_value, nobject_value, recall_value],
            feed_dict={
                logits: pred,
                tiny_yolo.class_labels: numpy.array([class_label]),
                tiny_yolo.class_masks: numpy.array([class_mask]),
                tiny_yolo.box_labels: numpy.array([box_label]),
                tiny_yolo.object_masks: numpy.array([object_mask])})
        sess.close()
        print(output)