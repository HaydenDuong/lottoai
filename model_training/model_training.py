from ultralytics import YOLO

# Retrieve pytorch file-format of the pre-trained YOLOv11 nano version
model = YOLO("yolo11n.pt")

# Fine-tune pre-trained model
if __name__ == '__main__':
    model.train(
        data = "data.yaml",
        device = 0,             # Use GPU instead of CPU
        batch = 20,
        workers = 1,            # Work directly on local computer
        epochs = 100,
        project = "C:\\Users\\Hayden Duong\\Desktop\\LottoAI\\model_training",           # Storing the trained model at this path
        name = "trained model"                                                          # Naming the folder for housing this trained model & related data
    )