# Download scripts from github


sudo mkdir -p /peach/tools
chown vagrant:vagrant /peach/tools

# Copy wget and curl to /peach/tools
sudo mkdir -p /etc/peach
sudo sed -e 's|/peach/tools:||g' -i /etc/environment && sed -e 's|PATH="\\(.*\\)"|PATH="/peach/tools:\\1"|g' -i /etc/environment
sudo sed -e 's|/peach/tools:||g' -i /etc/sudoers && sed -e 's|secure_path="\\(.*\\)"|secure_path="/peach/tools:\\1"|g' -i /etc/sudoers
