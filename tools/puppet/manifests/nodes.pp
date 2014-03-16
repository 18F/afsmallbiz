import "saber_mongodb"
import "saber_python"
import "saber_apache"

node "devel" {
  user {'saber':
    groups => ['sudo'],
    ensure => present,
    shell => '/bin/false',  #prevent user from logging in?
  }

  Exec {
      path => [ "/bin/", "/sbin/" , "/usr/bin/", "/usr/sbin/", "/usr/local/node/node-default/bin/" ],
      timeout   => 0,
  }

  class { 'apt':
    always_apt_update    => true,
    disable_keys         => undef,
    proxy_host           => false,
    proxy_port           => '8080',
    purge_sources_list   => false,
    purge_sources_list_d => false,
    purge_preferences_d  => false,
    update_timeout       => undef
  }

  #Set system timezone to UTC
  class { "timezone":
    timezone => 'UTC',
  }

  include saber_apache
  include saber_python
  include saber_mongodb

}
