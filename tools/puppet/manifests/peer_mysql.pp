#Install mysql server with overridden root password
class peer_mysql {

  class { '::mysql::server':
    root_password    => 'strongpassword',
    override_options => { 'mysqld' => { 'max_connections' => '1024' } }
  }

  #Create database
  mysql_database { 'peer':
    ensure  => 'present',
    charset => 'utf8',
  }->

  #Create user
  mysql_user { 'peeruser@127.0.0.1':
    ensure                   => 'present',
    max_connections_per_hour => '0',
    max_queries_per_hour     => '0',
    max_updates_per_hour     => '0',
    max_user_connections     => '0',
  } ->

  #Create user grants
  mysql_grant { 'peeruser@localhost/peer.*':
    ensure     => 'present',
    options    => ['GRANT'],
    privileges => ['ALL'],
    table      => 'peer.*',
    user       => 'peeruser@localhost',
  }

  #Install the mysql python bindings
  include "::mysql::bindings"
}
