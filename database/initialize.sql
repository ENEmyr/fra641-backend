create database fra641;

use fra641;

create table user (
    user_id bigint unsigned not null auto_increment,
    email varchar(300) not null,
    password char(128) not null,
    password_salt char(50) not null,
    first_name varchar(300) not null,
    last_name varchar(300) not null,
    role char(1) not null default '0', /* 0 = user, 1 = admin */
    primary key (user_id)
);

alter database fra641 character set utf8 collate utf8_unicode_ci;
