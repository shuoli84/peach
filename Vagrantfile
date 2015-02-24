# -*- mode: ruby -*-
# vi: set ft=ruby :
# vi: set shiftwidth=2 :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
  end

  config.vm.define 'peach-server' do |server|
    server.vm.network "forwarded_port", guest: 5000, host: 5000 
    server.vm.synced_folder ".", "/vagrant", disabled: true
    server.vm.synced_folder ".", "/peach"

    server.vm.provision "shell", inline: <<-SHELL
      cd /peach
      apt-get install -q -y python-pip
      pip install -r requirements.txt
      python app.py >> /peach/log.txt &
    SHELL
  end
end
