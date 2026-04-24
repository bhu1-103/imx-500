import numpy as np
from modlib.devices import AiCamera
from modlib.models import COLOR_FORMAT, MODEL_TYPE, Model
from modlib.models.post_processors import pp_od_yolo_ultralytics
from logic import GameState


class YOLO(Model):
    def __init__(self):
        super().__init__(
            model_file="yolo11n_imx_model/packerOut.zip",
            model_type=MODEL_TYPE.CONVERTED,
            color_format=COLOR_FORMAT.RGB,
            preserve_aspect_ratio=False,
        )
        self.labels = np.genfromtxt(
            "yolo11n_imx_model/labels.txt",
            dtype=str,
            delimiter="\n"
        )

    def post_process(self, output_tensors):
        return pp_od_yolo_ultralytics(output_tensors)


def main():
    device = AiCamera(frame_rate=30, headless=True)
    model = YOLO()
    device.deploy(model)

    game_state = GameState()

    last_command = "S"
    last_intensity = "NONE"

    print("System Standby. Only actions will be printed.", flush=True)

    with device as stream:
        for frame in stream:
            detections = frame.detections
            if detections is None or len(detections) == 0:
                continue

            valid = detections[detections.confidence > 0.1]
            if len(valid) == 0:
                continue

            command, intensity = game_state.process_frame(valid, model.labels)

            if command != last_command or intensity != last_intensity:
                if command == "S":
                    if last_command != "S":
                        print("DONE: Path Clear / Straight", flush=True)
                else:
                    print(f"{command} | {intensity}", flush=True)

                last_command = command
                last_intensity = intensity


if __name__ == "__main__":
    main()
