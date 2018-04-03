import numpy as np
import cv2
import cv2.aruco as aruco

def normalizar(ponto):
	'''
	Deixa o vetor homogeneo com z = 1
	'''
	ponto[0] = ponto[0] / ponto[2]
	ponto[1] = ponto[1] / ponto[2]
	ponto[2] = 1
	return ponto

# Loading Game Icons
gameIconNames = ["Apple", "Avocado", "Banana", "Broccoli", "Cheese", "Mushroom", "Potato Chips", "Sandwich"]
gameIcons = np.array([cv2.imread(name + ".png") for name in gameIconNames])

# Used for checking the orientation
# cv2.circle(gameIcons[0], (0, 0), 10, (0,0,255), -1)	#vermelho - canto superior esquerdo
# cv2.circle(gameIcons[0], (255, 0), 10, (0,255,0), -1)	#verde - canto superior direito
# cv2.circle(gameIcons[0], (255, 255), 10, (255,0,0), -1)	#azul - canto inferior direito
# cv2.circle(gameIcons[0], (0, 255), 10, (0,0,0), -1)	#preto - canto inferior esquerdo
# cv2.imshow(gameIconNames[0], gameIcons[0])

# Initializing some constant values
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
frameHeight, frameWidth, _ = frame.shape
dictionary = aruco.getPredefinedDictionary(aruco.DICT_6X6_50)
foundPairs = np.zeros(len(gameIcons))
points = 0

while(True):
    # Capture frame-by-frame
	ret, frame = cap.read()
	
	# Detecting markers
	markedCorners, markedIds, rejectedCandidates = aruco.detectMarkers(frame, dictionary)
	outputFrame = aruco.drawDetectedMarkers(frame, markedCorners, markedIds)
	
	# Calculating boundingbox and transformation matrices for processing
	matrix = []
	minX, minY, maxX, maxY = frameWidth-1, frameHeight-1, 0, 0
	if len(markedCorners) > 0:
		for cornArray in markedCorners:
			corners = cornArray[0]
			print("Corners:", corners)
			for corner in corners:
				if (corner[0] < minX):
					minX = int(corner[0])
				if (corner[0] > maxX):
					maxX = int(corner[0])
				if (corner[1] < minY):
					minY = int(corner[1])
				if (corner[1] > maxY):
					maxY = int(corner[1])
			
			# Generate transformation matrices
			matrix.append(cv2.getPerspectiveTransform(corners, np.float32([[0, 0], [255, 0], [255, 255], [0, 255]])))
		
		print(matrix)
	
		# Overlapping the markers with the icons
		for x in range(minX, maxX):
			for y in range(minY, maxY):
				for m in range(len(matrix)):
					[nX, nY, _] = normalizar(np.dot(matrix[m], np.array([x, y, 1])))
					if ((nX >= 0) and (nX < 256) and (nY >= 0) and (nY < 256)):
						outputFrame[y,x] = gameIcons[markedIds[m][0] % len(gameIcons)][int(nY),int(nX)]
		
		#If the game was finished, nothing here will happen
		if points != len(foundPairs):
			# Check for cheats
			if len(markedIds) > 2:
				points = 0
				foundPairs = np.zeros(len(gameIcons))
			# If not cheating check for pairs
			elif len(markedIds) == 2:
				if (markedIds[0][0] % len(gameIcons)) == (markedIds[1][0] % len(gameIcons)) and not foundPairs[markedIds[0][0] % len(gameIcons)]:
					foundPairs[markedIds[0][0] % len(gameIcons)] = 1
					points += 1
	
	#Display points
	pointText = "Found pairs: " + str(points) + "/" + str(len(foundPairs))
	if points == len(foundPairs):
		pointText = "You won the game!"
	cv2.putText(outputFrame, pointText, (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
	
    # Display the resulting frame
	cv2.imshow('Memory Game',outputFrame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()