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
    update_timeout       => undef
  }

  #Set system timezone to UTC
  class { "timezone":
    timezone => 'UTC',
  }

  package { 'curl':
    ensure    => installed,
  }

  include saber_python
  include saber_mongodb

}
