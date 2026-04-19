# game-agent-01

A custom designed Agent that can play the game [Road Fighter](https://en.wikipedia.org/wiki/Road_Fighter) using a custom DSP and multiple algorithms/rules.

## To-do

- [x] design custom dataset (Manually labelled ~350 images in Roboflow)
- [x] fine tune yolo 11n with custom dataset
- [x] quantize model to `int8`
- [x] convert and package model to make it work on IMX500
- [x] test model on pi zero 2 w
- [x] transfer metadata only instead of full video capture
- [x] apply logic on metadata -> make a basic rule based agent [achieved on April 19](../../timeline.md#Apr-19-2026)
- [x] game assistant -> suggests which direction to move to avoid crashing
- [ ] automatic game player

## Notes

- Using less number of samples (for training data and for quantization where ~300 images is needed) is fine for an use case like this, due to the following reasons
    1. The sprites of the game are very basic.
    2. There is no post processing in the game, therefore every single image will be the exact same.
    3. Yolo 11 is a very capable model that can catch the logic in the sprites with very few images to train.
