# -*- mode: ruby -*-
# vi: set ft=ruby :
# vi: set shiftwidth=2 :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"
  config.vm.synced_folder ".", "/vagrant", disabled: true
  config.vm.synced_folder ".", "/peach"
  config.vm.network "forwarded_port", guest: 5000, host: 5000 

  config.vm.provision "shell", inline: <<-SHELL
    cd /peach
    sudo apt-get install -q -y python-pip
    sudo pip install -r requirements.txt
    python app.py &
  SHELL
end
