import statistics


class GameState:
    def __init__(self):
        pass

    def process_frame(self, detections, labels):
        lane_centers = []
        enemies = []

        player_x = None
        player_top_y = None

        for i in range(len(detections)):
            bbox = detections.bbox[i]
            label = labels[int(detections.class_id[i])]

            x_center = (bbox[0] + bbox[2]) / 2.0

            if label == "Lane-Marking":
                lane_centers.append(x_center)

            elif label.startswith("Enemy"):
                enemies.append({
                    "x": x_center,
                    "bottom_y": bbox[3]
                })

            elif label == "Road-Fighter":
                player_x = x_center
                player_top_y = bbox[1]

        if not lane_centers or player_x is None:
            return "S", "NONE"

        center_line = statistics.median(lane_centers)
        player_lane = self._get_lane(player_x, center_line)

        command = "S"
        intensity = "NONE"

        for enemy in enemies:
            enemy_lane = self._get_lane(enemy["x"], center_line)

            is_ahead = 0.0 <= enemy["bottom_y"] < player_top_y
            same_lane = enemy_lane == player_lane

            if same_lane and is_ahead:
                command = self._get_evasion(player_lane)
                intensity = self._get_intensity(player_x, center_line)
                break

        return command, intensity

    def _get_lane(self, x, center_line):
        return "LEFT" if x < center_line else "RIGHT"

    def _get_evasion(self, player_lane):
        return "MOVE RIGHT" if player_lane == "LEFT" else "MOVE LEFT"

    def _get_intensity(self, player_x, center_line):
        distance = abs(center_line - player_x)
        return "0.2 (MORE)" if distance > 0.15 else "0.1 (LITTLE)"
