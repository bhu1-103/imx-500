import time
import numpy as np
from modlib.devices import AiCamera
from modlib.models import COLOR_FORMAT, MODEL_TYPE, Model
from modlib.models.post_processors import pp_od_yolo_ultralytics


class YOLO(Model):
    def __init__(self):
        super().__init__(
            model_file="yolo11n_imx_model/packerOut.zip",
            model_type=MODEL_TYPE.CONVERTED,
            color_format=COLOR_FORMAT.RGB,
            preserve_aspect_ratio=False,
        )

    def post_process(self, output_tensors):
        return pp_od_yolo_ultralytics(output_tensors)


def main():
    device = AiCamera(frame_rate=30, headless=True)
    model = YOLO()
    device.deploy(model)

    print("Raw metadata stream (detections + latency)\n", flush=True)

    prev_time = time.time()

    with device as stream:
        for frame in stream:
            now = time.time()
            latency_ms = (now - prev_time) * 1000
            fps = 1.0 / (now - prev_time) if (now - prev_time) > 0 else 0
            prev_time = now

            detections = frame.detections

            print("---- FRAME ----")
            print(f"Latency: {latency_ms:.2f} ms | FPS: {fps:.2f}")

            if detections is None:
                print("Detections: None\n")
                continue

            print(f"Detections count: {len(detections)}")

            for det in detections:
                print(det)

            print()  # spacing


if __name__ == "__main__":
    main()
