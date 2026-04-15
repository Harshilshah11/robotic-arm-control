# 57:06 
import cv2

def rescale_frame(frame, scale=0.75):
    """Rescale an image frame by a given scale factor."""
    if frame is None:
        raise ValueError("Input frame is None. Check image path.")

    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width, height)

    return cv2.resize(frame, dimensions, interpolation=cv2.INTER_AREA)
    
def main():
    # Read image
    img = cv2.imread("airplane.jpg")

    if img is None:
        print("Error: Could not load image. Check file path.")
        return

    # Rescale image
    new_img = rescale_frame(img, 0.5)

    # Show images
    cv2.imshow("Original Image", img)
    cv2.imshow("Rescaled Image", new_img)

    # Wait for key press
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
    
# cap=cv2.VideoCapture(0)    
# def changeRes(width,height):
#     cap.set(3,width)   
#     cap.set(4,height)         