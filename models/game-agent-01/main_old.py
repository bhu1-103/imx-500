import time
import numpy as np

from modlib.devices import AiCamera
from modlib.models import COLOR_FORMAT, MODEL_TYPE, Model
from modlib.models.post_processors import pp_od_yolo_ultralytics

from logic_old import GameState
import fake_keyboard_old as kb

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
    device = AiCamera(frame_rate=24, headless=True) #30 and 28 made YOLO slow and choose 14 or 15 FPS (HALF)
    model = YOLO()
    device.deploy(model)

    game_state = GameState()
    
    print("System starting...", flush=True)

    TAP_DURATION = 0.040 
    
    current_speed_mode = "NONE" 
    last_steer_log = "NONE"

    with device as stream:
        try:
            for frame in stream:
                detections = frame.detections
                
                if detections is None or len(detections) == 0:
                    continue

                valid = detections[detections.confidence > 0.1]
                if len(valid) == 0:
                    continue

                command, speed_command = game_state.process_frame(valid, model.labels)

                if speed_command != current_speed_mode:
                    if speed_command == "ACCEL":
                        #kb.press("d", "f")
                        kb.press("d")

                    else:
                        #kb.release("d", "f")
                        kb.release("d")
                    current_speed_mode = speed_command

                if command == "MOVE LEFT":
                    if last_steer_log != "LEFT":
                        print("<< TAP LEFT", flush=True)
                        last_steer_log = "LEFT"
                    kb.press("LEFT")
                    time.sleep(TAP_DURATION)
                    kb.release("LEFT")
                elif command == "MOVE RIGHT":
                    if last_steer_log != "RIGHT":
                        print("TAP RIGHT >>", flush=True)
                        last_steer_log = "RIGHT"
                    kb.press("RIGHT")
                    time.sleep(TAP_DURATION)
                    kb.release("RIGHT")
                elif command == "S":
                    if last_steer_log != "S":
                        last_steer_log = "S"
                    kb.release("LEFT", "RIGHT")

        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            kb.release()

if __name__ == "__main__":
    main()

