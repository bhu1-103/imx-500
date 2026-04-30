# IMX500

Experiments with running custom YOLO and pose detection models directly on the Sony IMX500 intelligent vision sensor.

## Latest work

Made an agent play Road Fighter using USB HID, IMX500 and some rules. Check [here](https://github.com/bhu1-103/imx-500/tree/main/models/game-agent-01)
I have a writeup of it on my [website](https://8hu.one/projects/auto_game_player/index.html) as well. This is better documented.

## To-do

- [x] get yolo working
- [x] make the agent play a basic game
- [ ] transparent display (ordered, arriving in a few days)
- [ ] make it portable, replace powerbank with lipo battery (maybe powerbank is better to avoid brownouts, etc)

---

## Notes & Logs

- [Timeline of experiments](./timeline.md)
- [Dataset prepration for fine tuning](./custom-dataset.md)
- [Hacks and undocumented behavior](./hacks.md)
- [Training a custom ImageNet model to classify cats and dogs](./custom-model-dataset.md)
- [Fine-tuning yolo-11n on custom dataset](./yolo-guide.md)

---

## Models & Utilities

### Classic YOLO
- [`./models/classic-yolo/README.md`](./models/classic-yolo/classic-yolo.py)

### Pose Detection
- [`./models/pose-detection/README.md`](./models/pose-detection/json-ify.py)

### Custom ImageNet model training with custom dataset
- [`./models/custom-imagenet/README.md`](./models/custom-imagenet/train.py)

### Reinforcement Learning based Game Playing agent
- [`./models/game-agent-01/README.md`](./models/game-agent-01)
