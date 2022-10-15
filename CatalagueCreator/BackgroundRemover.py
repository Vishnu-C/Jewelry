import os
from rembg import remove

def RemoveBackgrounds(image_file_path):
    print("image name :", image_file_path)
    output_path = image_file_path + '_BGRemoved.jpg'

    with open(image_file_path, 'rb') as i:
        with open(output_path, 'wb') as o:
            input = i.read()
            output = remove(input)
            o.write(output)


# Defining main function
def main():
    # Inputs
    selected_images_folder_path = "D:/Work/projects/Jewelry/CAD Files/PNDNT RING.IMG/PNDNT RING.ING"

    for imageFilename in os.listdir(selected_images_folder_path):
        if (imageFilename.endswith(".png") or imageFilename.endswith(".jpg") or imageFilename.endswith(".jpeg")):
            filePath = os.path.join(selected_images_folder_path, imageFilename)
            RemoveBackgrounds(filePath)
    
if __name__ == "__main__":
    main()