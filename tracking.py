import cv2
print('start program')
cap = cv2.VideoCapture(0)
print('start capturing')
roi_stage = 0
while True:
    _, frame = cap.read()
    
    if roi_stage == 0 or key == ord('o'):
        # need to create new tracker when the roi not found
        tracker = cv2.TrackerCSRT_create()  # :-(
        roi = cv2.selectROI('tracker',frame)
        print(roi)
        tracker.init(frame, roi)
        roi_stage = 1
    
    success, roi = tracker.update(frame)


    canvas = cv2.rectangle(frame
            , (int(roi[0]),int(roi[1]),int(roi[2]),int(roi[3]))
            , (255,0,0), 2)
    canvas = cv2.circle(frame
            , (int((roi[0]+roi[2])/2),int((roi[1]+roi[3])/2)),5
            , (255,0,0), 2)
    cv2.imshow('this camera', canvas)
    t = 1
    if not success:
        t = 0
    key = cv2.waitKey(t)  
    if key == ord('a'):
        break
cap.release()
cv2.destroyAllWindows()