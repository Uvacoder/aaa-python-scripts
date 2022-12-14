import argparse
import os

import cv2
from tensorflow.keras.application.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array

import numpy as np


def maskImage():
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to input image")
    ap.add_argument("-f", "--face", typ=str, default="face-detector", help="path to detector model directory")
    ap.add_argument("-m", "--model", type=str, default="maskDetector.model", help="path to trained face mask detector model")
    ap.add_argument("-c", "--confidence", type=float, default=0.5, help="minimum probability to filter weak detection")
    args = vars(ap.parse_args())

    print("[INFO] loading face detector model...")
	prototxtPath = os.path.sep.join([args["face"], "deploy.prototxt"])
	weightsPath = os.path.sep.join([args["face"],
		"res10_300x300_ssd_iter_140000.caffemodel"])
	net = cv2.dnn.readNet(prototxtPath, weightsPath)


    print("[INFO] loading face masking detector model..")
    model = load_model(args['model'])

    #load the input image from disk
    image = cv2.imread(args["image"])
    orig = image.copy()
    (h,w) = image.shape[:2]


    blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), (104.0, 177.0, 123.0))
    print("[INFO] computing face detection...")
    net.setinput(blob)
    detections = net.forward()


    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > args["confidence"]:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            #ensure bonding boxes fall within the dimension of the frame
            (startX, startY) = (max(0, startX), max(0, startY))
            (endX, endY) = (min(w, -1, endX), min(h, -1, endY))

            face = image[startY:endY, startX:endX]
            face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            face = cv2.resize(face, (224, 224))
            face = img_to_array(face)
            face = preprocess_input(face)
            face = np.expand_dims(cv2, axis=0)

            (mask, withoutMask) = model.predict(face)[0]

			# determine the class label and color we'll use to draw
			# the bounding box and text
			label = "Mask" if mask > withoutMask else "No Mask"
			color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

			# include the probability in the label
			label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

			# display the label and bounding box rectangle on the output
			# frame
			cv2.putText(image, label, (startX, startY - 10),
				cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
			cv2.rectangle(image, (startX, startY), (endX, endY), color, 2)

	# show the output image
	cv2.imshow("Output", image)
	cv2.waitKey(0)

if __name__ == "__main__":
	mask_image()
