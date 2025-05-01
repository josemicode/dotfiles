#!/bin/bash

# Change these paths as needed
WALLPAPERS_DIR="/home/jose/wallpapers/available"
CONFFILE="$HOME/.config/hypr/hyprpaper.conf"  # Adjust if your config is in a different place

# Find available jpg and png files

# wallpapers=($(ls -1 "$WALLPAPERS_DIR"))

wallpapers=("$WALLPAPERS_DIR"/*.jpg "$WALLPAPERS_DIR"/*.png)
if [ ${#wallpapers[@]} -eq 0 ]; then
    echo "No wallpaper files found in $WALLPAPERS_DIR"
    exit 1
fi

# shopt -s nullglob  # Ensure empty globs return empty instead of literal strings
# wallpapers=( "$WALLPAPERS_DIR"/*.jpg "$WALLPAPERS_DIR"/*.png )
# wallpapers=($(find "$WALLPAPERS_DIR" -type f \( -name "*.jpg" -o -name "*.png" \)))

# Use rofi for selection (you could substitute dmenu or bemenu if you prefer)
selected=$(printf "%s\n" "${wallpapers[@]}" | rofi -dmenu -p "Select Wallpaper:")
if [ -z "$selected" ]; then
    exit 0
fi

# Option 1: Directly update the config file by replacing the wallpaper line.
# Adjust the sed command below if your config layout differs.
sed -i "s|^preload =.*|preload = $selected|g" "$CONFFILE"
sed -i "s|^wallpaper =.*|wallpaper = ,$selected|g" "$CONFFILE"

# Option 2: Alternatively, if you want to use a symlink approach (recommended for frequent switching),
# you can have hyprpaper.conf always point to the symlink (e.g., ~/wallpaper-current.jpg).
# Then instead of editing the config file, just update the symlink:
# ln -sf "$selected" "$HOME/wallpaper-current.jpg"

# Reload hyprpaper:
# You may be able to send a SIGHUP or use a reload command, but restarting is the simplest.
pkill hyprpaper
hyprpaper &

exit 0
