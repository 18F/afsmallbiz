class saber_python {

    class { 'python':
      version    => '2.7',
      pip        => true,
      dev        => true,
      virtualenv => false,
      gunicorn   => true,
    }

   python::requirements { '/vagrant/requirements.txt': }

    python::gunicorn { 'vhost':
      ensure      => present,
      mode        => 'wsgi',
      dir         => '/vagrant',
      bind        => '192.168.33.10:80',
      environment => 'prod',
    }
}
