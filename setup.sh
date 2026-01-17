#!/bin/bash

ln -sf ~/dotfiles/.bashrc ~/.bashrc
ln -sf ~/dotfiles/hyprland.conf ~/.config/hypr/hyprland.conf
ln -sf ~/dotfiles/hyprpaper.conf ~/.config/hypr/hyprpaper.conf
ln -sf ~/dotfiles/neofetch ~/.config/neofetch
ln -sf ~/dotfiles/wallpapers/wall_selector.sh ~/wallpapers/wall_selector.sh
ln -sf ~/dotfiles/vscodium/User ~/.config/VSCodium/User
ln -sf ~/dotfiles/zed ~/.config/zed

# Add other symlinks as needed

echo "Dotfiles setup complete!"
