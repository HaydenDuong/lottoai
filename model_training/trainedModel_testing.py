from ultralytics import YOLO

# Retrieve generated fine-tuned model
model = YOLO("C:\\Users\\Hayden Duong\\Desktop\\LottoAI\\model_training\\trained model2\\weights\\best.pt")

# Run detection on the subfolder "test" of "dataset" folder
results = model.predict (
    
    # Path to folder contain images for testing
    source = "C:\\Users\\Hayden Duong\\Desktop\\LottoAI\\model_training\\raw_images\\new_images",
    
    # Save images with labeling box around Region of Interest (ROI)
    save = True,
    
    # Save the coordination of both starting & ending points of labeled-ROI
    save_txt = True,
    
    # Crop ROI through YOLO built-in function
    save_crop = True,
    
    # Location & name given for generated results folder
    project = "C:\\Users\\Hayden Duong\\Desktop\\LottoAI\\model_training",
    name = "prediction"
)