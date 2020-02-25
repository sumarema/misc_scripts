import csv
import logging
import argparse
import sys

from PIL import Image, ImageChops

log = logging.getLogger(__name__)

import cv2
from timeit import default_timer as timer


def _get_images_list_from_csv(csv_file_name):
    with open(csv_file_name) as csv_file:
        first_image_list = []
        second_image_list = []
        reader = csv.DictReader(csv_file)
        for row in reader:
            first_image = row['image1']
            second_image = row['image2']
            first_image_list.append(first_image)
            second_image_list.append(second_image)
        return first_image_list, second_image_list


def _resolution_diff(first_image, second_image):
    print("FS: {0}".format(first_image.shape))
    print("SS: {0}".format(second_image.shape))
    difference = cv2.subtract(first_image.shape, second_image.shape)
    r, g, b = difference
    if int(r[0]) == 0 and int(g[0]) == 0 and int(b[0]) == 0:
        print("All Resolutions same")
        print("Resolution Score: {0}".format(difference))
    else:
        print("Image Score : {0}".format(difference))


def _pixel_compare(first, second):
    first_image = Image.open(first)
    second_image = Image.open(second)
    r1, g1, b1 = first_image.getdata()[0], first_image.getdata()[1], first_image.getdata()[2]
    band1 = first_image.getbands()
    r2, g2, b2 = second_image.getdata()[0], second_image.getdata()[1], second_image.getdata()[2]
    print("First Image Data : {0} : R: {1}, G: {2}, B: {3}".format(first, r1, g1, b1))
    print("Second Image Data : {0} : R: {1}, G: {2}, B: {3}".format(second, r2, g2, b2))
    difference = ImageChops.difference(first_image, second_image)
    if difference is None:
        print("Pixel Difference Score : 1")
    else:
        print("Pixel Difference Score : {0}".format(difference.getbbox()))
        print("Pixel Histogram Score : {0}".format(difference.histogram()))
        # print(help(difference))


def _difference_percentage(first, second):
    first_image = Image.open(first)
    second_image = Image.open(second)
    print("Modes : First : {} : Second : {}".format(first_image.mode, second_image.mode))
    if first_image.mode == second_image.mode:
        print("Can Process with regular comparision")
    else:
        print("Both Belong to different Modes so need to convert to compare")


def _compare_percentage(first, second):
    first_image = Image.open(first).convert("LA")
    second_image = Image.open(second).convert("LA")
    combined_data = zip(first_image.getdata(), second_image.getdata())
    difference = sum(abs(c1 - c2) for p1, p2 in combined_data for c1, c2 in zip(p1, p2))
    comps = first_image.size[0] * first_image.size[1] * 3
    percentage = difference / 255.0 * 100 / comps
    return percentage


def _compare_image_data(first_image_list, second_image_list):
    elapsed_list = []
    percentages = []
    for first, second in zip(first_image_list, second_image_list):
        start_time = timer()
        log.info("Comparing {0} and {1}".format(first, second))
        diff_percent = _compare_percentage(first, second)
        percentages.append("{0:.4f}".format(diff_percent))
        log.info("Percentage of Difference : {0:.4f} ".format(diff_percent))
        end_time = timer()
        elapsed_time = end_time - start_time
        elapsed_list.append("{0:.4f}".format(elapsed_time))
        log.info("Elapsed Time : {0:.4f}".format(elapsed_time))
        log.info(20 * "==")
    return elapsed_list, percentages


def _generate_csv_file(first_images_list, second_images_list, percentage_list, elapsed_times, file_name):
    write_file_name = file_name.split(".csv")[0]
    write_file_name = write_file_name + "_result.csv"
    with open(write_file_name, 'w') as write_file:
        keys = ['image1', 'image2', 'similar', 'elapsed']
        writer = csv.DictWriter(write_file, fieldnames=keys)
        writer.writeheader()
        for image1, image2, similar, elapsed in zip(first_images_list, second_images_list, percentage_list,
                                                    elapsed_times):
            writer.writerow({'image1': image1, 'image2': image2, 'similar': similar, 'elapsed': elapsed})


def image_diff(file_name, **kwargs):
    """ image_diff takes CSV input of paired Images and show the percentage of differences between them.
    The result will be published into workspace with <file_name>_result.csv.
    """
    one_list, two_list = _get_images_list_from_csv(file_name)
    elapsed_list, percentages = _compare_image_data(one_list, two_list)
    _generate_csv_file(one_list, two_list, percentages, elapsed_list, file_name)


def _get_args(args):
    """Takes file name as Argument and passes to image_diff function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--loglevel', dest="loglevel",
                        choices=['INFO', 'DEBUG', 'WARN', 'ERROR'],
                        default='INFO')
    subparsers = parser.add_subparsers()
    parser_show_image_difference_percent = subparsers.add_parser('image_diff',
                                                                 description=image_diff.__doc__,
                                                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    parser_show_image_difference_percent.add_argument('-f', '--file_name',
                                                      dest="file_name",
                                                      required=True)
    parser_show_image_difference_percent.set_defaults(func=image_diff)
    args = parser.parse_args(args)
    return args


def main():
    args = _get_args(sys.argv[1:])
    logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                        level=logging.getLevelName(args.loglevel))
    log.setLevel(logging.DEBUG)
    log.info("Logging set to level: " + str(args.loglevel.upper()))
    args.func(**vars(args))


if __name__ == '__main__':
    main()
