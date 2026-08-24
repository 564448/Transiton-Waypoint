import argparse
import math
import os

def rotate_point(x, y, angle_degrees):
    """Rotate point (x, y) around the origin by the given angle (counter-clockwise positive / clockwise negative)."""
    angle_radians = math.radians(angle_degrees)
    cos_a = math.cos(angle_radians)
    sin_a = math.sin(angle_radians)

    # Rotation matrix formula
    x_new = x * cos_a - y * sin_a
    y_new = x * sin_a + y * cos_a
    return x_new, y_new

def transform_file(input_file, output_file, file_type, orig_lat, orig_lon, target_lat, target_lon, rotation_angle):
    # Average radius of the Earth (meters)
    R = 6378137.0

    if not os.path.exists(input_file):
        print(f"Input file not found: {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        print("File is empty")
        return

    print(f"[{file_type.upper()}] Original field home point: Lat {orig_lat}, Lon {orig_lon}")
    print(f"Moving to new field home point: Lat {target_lat}, Lon {target_lon} with rotation {rotation_angle} degrees")

    new_lines = []

    # Start converting and rotating coordinates, measured relative to the original home point
    if file_type == 'wp':
        new_lines.append(lines[0]) # Keep header
        for line in lines[1:]:
            parts = line.strip().split('\t')
            if len(parts) < 10:
                new_lines.append(line)
                continue
            try:
                lat = float(parts[8])
                lon = float(parts[9])

                if lat == 0.0 and lon == 0.0:
                    new_lines.append(line)
                    continue

                # Convert coordinate difference to meters (dx, dy) relative to the original home point
                d_lat = math.radians(lat - orig_lat)
                d_lon = math.radians(lon - orig_lon)

                dy = d_lat * R
                dx = d_lon * R * math.cos(math.radians(orig_lat))

                # Rotate
                dx_rot, dy_rot = rotate_point(dx, dy, rotation_angle)

                # Convert back to Lat/Lon by adding onto the new home point
                new_lat = target_lat + math.degrees(dy_rot / R)
                new_lon = target_lon + math.degrees(dx_rot / (R * math.cos(math.radians(target_lat))))

                parts[8] = f"{new_lat:.8f}"
                parts[9] = f"{new_lon:.8f}"
                new_lines.append('\t'.join(parts) + '\n')
            except ValueError:
                new_lines.append(line)

    elif file_type == 'poly':
        for line in lines:
            if line.strip().startswith('#') or not line.strip():
                new_lines.append(line) # Keep comment/blank line structure
                continue

            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    lat = float(parts[0])
                    lon = float(parts[1])

                    # Convert coordinate difference to meters (dx, dy) relative to the original home point
                    d_lat = math.radians(lat - orig_lat)
                    d_lon = math.radians(lon - orig_lon)

                    dy = d_lat * R
                    dx = d_lon * R * math.cos(math.radians(orig_lat))

                    # Rotate
                    dx_rot, dy_rot = rotate_point(dx, dy, rotation_angle)

                    # Convert back to Lat/Lon by adding onto the new home point
                    new_lat = target_lat + math.degrees(dy_rot / R)
                    new_lon = target_lon + math.degrees(dx_rot / (R * math.cos(math.radians(target_lat))))

                    parts[0] = f"{new_lat:.8f}"
                    parts[1] = f"{new_lon:.8f}"
                    new_lines.append(' '.join(parts) + '\n')
                except ValueError:
                    new_lines.append(line)
            else:
                new_lines.append(line)

    # Save the new file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Done! New file saved to: {output_file}\n")


# ==========================================
# CLI setup
# ==========================================
def parse_latlon(value, flag_name):
    parts = value.split(',')
    if len(parts) != 2:
        raise argparse.ArgumentTypeError(
            f"{flag_name} must be in the format lat,lon, e.g. 52.780562,-0.707918 (got: {value})"
        )
    try:
        return float(parts[0]), float(parts[1])
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{flag_name} must be numeric lat,lon, e.g. 52.780562,-0.707918 (got: {value})"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Translate and rotate Waypoint/Polygon file coordinates to a new home point"
    )
    parser.add_argument('--mode', required=True, choices=['wp', 'poly'],
                         help="File type: 'wp' for Waypoint or 'poly' for Polygon")
    parser.add_argument('--input', required=True, help="Input file path")
    parser.add_argument('--output', required=True, help="Output file path")
    parser.add_argument('--orig', required=True,
                         help="Original field home point, format lat,lon, e.g. 52.780562,-0.707918")
    parser.add_argument('--target', required=True,
                         help="New field home point, format lat,lon, e.g. 52.623818,-1.1750744")
    parser.add_argument('--rotation', type=float, default=0.0,
                         help="Rotation angle in degrees (positive = counter-clockwise, negative = clockwise), default 0")

    args = parser.parse_args()

    orig_lat, orig_lon = parse_latlon(args.orig, '--orig')
    target_lat, target_lon = parse_latlon(args.target, '--target')

    transform_file(args.input, args.output, args.mode,
                    orig_lat, orig_lon, target_lat, target_lon, args.rotation)
