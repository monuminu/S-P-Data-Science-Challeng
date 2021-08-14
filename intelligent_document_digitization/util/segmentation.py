import os
import numpy as np 
import cv2
import pandas as pd 
import logging
logger = logging.getLogger()

def get_image_from_words(words, width, height):
    """
        Create page image from page words
    """
    page_image_undialated = np.zeros((height, width), dtype = np.uint8)
    for word in words:
        x0 = int(word["x0"])
        y0 = int(word["top"])
        x1 = int(word["x1"])
        y1 = int(word["bottom"])
        page_image_undialated[y0 : y1, x0 : x1] = 255
    ker = np.ones((1, int(0.01 * height)), dtype = np.uint8)
    page_image = cv2.dilate(page_image_undialated, ker , iterations = 1)
    return page_image

def cut_segment(page_image):
    """
        Cut the page matrix into segments
        >>> cut_segment(np.random.randint(2, size=(612, 792)))
    """
    binary = np.any(page_image, axis = 1).astype("uint8")
    _, contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    regions = []
    for contour in contours:
        points  = [list(x) for xx in contour for x in xx]
        points = np.array(points)
        points = points[:, 1]
        if len(points) == 1:
            regions.append([points[0], points[0] + 1])
        else:
            points[1] += 1
            regions.append(list(points))
    regions = sorted(regions, key = lambda x : x[0])
    return regions

def get_lr_tb_cuts(page_image):
    """
        Get the top to bottom segments and lef to right segments
        >>> get_lr_tb_cuts(np.random.randint(2, size=(612, 792)))
    """
    tb_cuts = cut_segment(page_image)
    lr_cuts = []
    for tb_cut in tb_cuts:
        lr_cut = cut_segment(page_image[tb_cut[0] : tb_cut[1], :].T)
        lr_cuts.append(lr_cut)
    return tb_cuts, lr_cuts

def label_segment(tb_cuts, lr_cuts, median_word_height):
    """
        Label the segments if they are TABLE or PARA
    """
    print("median_word_height :", median_word_height)
    segments = []
    prev_label = "PARA"
    prev_start = 0
    prev_stop = 0
    for lr_cut, tb_cut in zip(lr_cuts, tb_cuts):
        if len(lr_cut) > 2:
            cur_label = "PARA"
        else:
            cur_label = "PARA"
        if prev_label == cur_label:
            if tb_cut[0] - prev_stop < median_word_height:
                cur_start = segments[-1][0]
                segments.pop()
                segments.append([cur_start, tb_cut[1], cur_label])
            else:
                segments.append([tb_cut[0], tb_cut[1], cur_label])
        prev_label = cur_label
        prev_start = tb_cut[0]
        prev_stop = tb_cut[1]
    return segments

def debug_segmentation(page, width, height, segments, image_file):
    page_image = page.to_image(resolution = 300)
    segments_to_draw = [[0, segment[0], width, segment[1]] for segment in segments]
    page_image.draw_rects(segments_to_draw)
    page_image.save(image_file)
