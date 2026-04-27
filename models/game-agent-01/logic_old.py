import statistics

class GameState:
    def __init__(self):
        self.prev_enemies = {}
        self.last_center_line = 0.5  
        self.current_steering_state = "S" 
        
        self.locked_player_y = None
        self.locked_player_height = None
        
        # STABILIZATION TRACKER
        self.recovery_frames = 0 

    def process_frame(self, detections, labels):
        lane_markings = []
        enemies = []
        player_x = player_top_y = player_bottom_y = player_width = None

        for i in range(len(detections)):
            bbox = detections.bbox[i]
            label = labels[int(detections.class_id[i])]
            x_center = (bbox[0] + bbox[2]) / 2.0
            width = bbox[2] - bbox[0]

            if label == "Lane-Marking":
                lane_markings.append({"x": x_center, "y": bbox[1]})
            elif label.startswith("Enemy"):
                enemies.append({
                    "x": x_center, "y": bbox[3], 
                    "top_y": bbox[1], "width": width, "id": i
                })
            elif label == "Road-Fighter":
                player_x, player_top_y, player_bottom_y, player_width = x_center, bbox[1], bbox[3], width

        if player_x is None or player_width is None:
            return "S", "ACCEL"

        player_height = player_bottom_y - player_top_y

        if self.recovery_frames > 0:
            self.recovery_frames -= 1
            self.current_steering_state = "S"
            return "S", "BRAKE"

        # Spin-out failsafe: If our width is larger than our height, we are sliding sideways.
        if player_width > (player_height * 1.1):
            self.recovery_frames = 8  # Force a brake to use Trick no. 1
            self.current_steering_state = "S"
            return "S", "BRAKE"

        for enemy in enemies:
            enemy_h = enemy["y"] - enemy["top_y"]
            # YOLO jitter, 85% noise filter
            h_overlap = abs(player_x - enemy["x"]) < ((player_width + enemy["width"]) / 2.0) * 0.85
            v_overlap = abs(((player_top_y + player_bottom_y)/2.0) - ((enemy["top_y"] + enemy["y"])/2.0)) < ((player_height + enemy_h) / 2.0) * 0.85
            
            if h_overlap and v_overlap:
                # Trick no. 1 on yt video
                self.recovery_frames = 10 
                self.current_steering_state = "S"
                return "S", "BRAKE"
        
        if self.locked_player_y is None:
            self.locked_player_y = player_top_y
            self.locked_player_height = player_height
        
        p_top_y = self.locked_player_y
        p_bot_y = self.locked_player_y + (self.locked_player_height * 1.05)
        p_height = self.locked_player_height

        if lane_markings:
            lane_markings.sort(key=lambda l: l["y"], reverse=True)
            center_line = statistics.mean([l["x"] for l in lane_markings[:2]])
            self.last_center_line = center_line
        else:
            center_line = self.last_center_line 

        road_width = player_width * 6
        safe_road_left = (center_line - road_width/2) + (player_width * 0.15)
        safe_road_right = (center_line + road_width/2) - (player_width * 0.15)

        blocked = []
        current_enemies_state = {}

        for enemy in enemies:
            if enemy["top_y"] >= p_bot_y:
                continue 

            eid = enemy["id"]
            vx = 0
            if eid in self.prev_enemies:
                vx = (enemy["x"] - self.prev_enemies[eid]["x"])
            
            # Jitter Filter
            if abs(vx) < (player_width * 0.15):
                vx = 0

            pred_x = enemy["x"] + (vx * 2) 

            # My dumb code thought overtaking an enemy car is enough and then moves towards the enemy, not realizing the enemy was just by the side.
            half_block = (enemy["width"] / 2.0) + (player_width / 2.0) + (player_width * 0.05)
            blocked.append((pred_x - half_block, pred_x + half_block))
            
            enemy["vx"] = vx
            current_enemies_state[eid] = enemy

        self.prev_enemies = current_enemies_state

        blocked.sort()
        merged = []
        for s, e in blocked:
            if not merged or s > merged[-1][1]:
                merged.append([s, e])
            else:
                merged[-1][1] = max(merged[-1][1], e)

        gaps = []
        curr = safe_road_left
        for s, e in merged:
            if s > curr: gaps.append((curr, s))
            curr = max(curr, e)
        if curr < safe_road_right: gaps.append((curr, safe_road_right))

        best_gap = None
        best_score = float("inf")
        
        # Pass through narrow gaps... risky tbh...
        min_gap_width = player_width * 0.95 

        for gs, ge in gaps:
            gap_width = ge - gs
            if gap_width < min_gap_width:
                continue
            
            if player_x < gs:
                dist_to_gap = gs - player_x 
            elif player_x > ge:
                dist_to_gap = player_x - ge 
            else:
                dist_to_gap = 0 
            
            score = dist_to_gap - (gap_width * 0.1)
            
            if score < best_score:
                best_score, best_gap = score, (gs, ge)

        if best_gap is None:
            # Emergency back off as there are a lot of cars and no (safe/predictible) space to pass through
            self.current_steering_state = "S"
            return "S", "BRAKE"

        # We found a gap. Do not leave your foot off the gas pedal.
        speed_command = "ACCEL"

        margin = player_width * 0.1 
        s_left = best_gap[0] + margin
        s_right = best_gap[1] - margin

        # Steer towards the gap if not already.
        if player_x < s_left:
            command = "MOVE RIGHT"
        elif player_x > s_right:
            command = "MOVE LEFT"
        else:
            command = "S"

        self.current_steering_state = command
        return command, speed_command

