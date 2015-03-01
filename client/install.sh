# Download scripts from github
mkdir -p /tmp/peach

# We should use the system default wget instead of peach one
echo "Strip peach path out of PATH, we need the original wget"
PATH=$(echo "$PATH" | sed -e 's|/peach/tools:||g')

echo "Getting scripts from github/shuoli84/peach/master"
wget https://raw.githubusercontent.com/shuoli84/peach/master/client/scripts/command.py -O /tmp/peach/command.py -q
wget https://raw.githubusercontent.com/shuoli84/peach/master/client/scripts/curl -O /tmp/peach/curl -q
wget https://raw.githubusercontent.com/shuoli84/peach/master/client/scripts/wget -O /tmp/peach/wget -q

# Create peach scripts folder
echo "Create /peach/tools"
mkdir -p /peach/tools
chown vagrant:vagrant /peach/tools

echo "Copy wget and curl to /peach/tools"
cp /tmp/peach/command.py /peach/tools/
cp /tmp/peach/curl /peach/tools/
cp /tmp/peach/wget /peach/tools/

echo "chmod of scripts"
chmod +x /peach/tools/wget
chmod +x /peach/tools/curl

echo "Setting path to /etc/environment"
sed -e 's|/peach/tools:||g' -i /etc/environment 
sed -e 's|PATH="\(.*\)"|PATH="/peach/tools:\1"|g' -i /etc/environment

echo "Add path to /etc/sudoers secure_path"
sed -e 's|/peach/tools:||g' -i /etc/sudoers 
sed -e 's|secure_path="\(.*\)"|secure_path="/peach/tools:\1"|g' -i /etc/sudoers

echo "Generate the conf folder"
mkdir -p /etc/peach
