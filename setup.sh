#!/bin/bash

ln -sf ~/dotfiles/.bashrc ~/.bashrc
ln -sf ~/dotfiles/hyprland.conf ~/.config/hypr/hyprland.conf
ln -sf ~/dotfiles/hyprpaper.conf ~/.config/hypr/hyprpaper.conf
ln -sf ~/dotfiles/neofetch ~/.config/neofetch

# Add other symlinks as needed

echo "Dotfiles setup complete!"
