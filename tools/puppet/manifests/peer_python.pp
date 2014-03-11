class peer_python {

    class { 'python':
      version    => '2.7',
      pip        => true,
      dev        => true,
      virtualenv => false,
      gunicorn   => true,
    }

#    python::virtualenv { '/home/vagrant/virtenv':
#      ensure       => present,
#      version      => 'system',
#      requirements => '/vagrant/requirements.txt',
#      systempkgs   => true,
#      distribute   => true,
#      cwd          => '/vagrant',
#      timeout      => 0,
#    }

   python::requirements { '/vagrant/requirements.txt':
#      virtualenv => '/var/www/project1',
#      proxy      => 'http://proxy.domain.com:3128',
#      owner      => 'appuser',
#      group      => 'apps',
    }

    python::gunicorn { 'vhost':
      ensure      => present,
#      virtualenv  => '/home/vagrant/virtenv',
      mode        => 'wsgi',
      dir         => '/vagrant',
      bind        => '192.168.33.10:80',
      environment => 'prod',
      template    => 'python/gunicorn.erb',
    }
}
