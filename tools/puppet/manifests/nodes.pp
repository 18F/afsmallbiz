import "peer_mysql"
import "peer_python"

node "devel" {
  user {'peer':
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

  include peer_python
  include peer_mysql


#  exec { 'start':
#    command   => "/home/vagrant/forever start app.js",
#    cwd       => "/vagrant",
#    unless    => "ps -ef | grep '[f]orever'"
#  }
}
