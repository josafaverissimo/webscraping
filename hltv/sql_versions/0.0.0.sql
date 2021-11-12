use hltv;

drop table if exists teams_stats;
drop table if exists maps;
drop table if exists teams;

create table maps(
	id int(11) unsigned not null primary key auto_increment,
	name varchar(255) not null
	
);

create table teams(
	id int(11) unsigned not null primary key auto_increment,
	name varchar(255) not null,
	created_at timestamp not null default current_timestamp
);

create table teams_stats(
	id int(11) unsigned not null primary key auto_increment,
	team_id int(11) unsigned not null,
	map_id int(11) unsigned not null,
	times_played int(11) not null,
	ct_rate_win decimal(5,3) not null,
	tr_rate_win decimal(5,3) not null,
	both_rate_win decimal(5,3) not null,
	created_at timestamp not null default current_timestamp,
	constraint team_id_fk foreign key (team_id) references teams(id),
	constraint map_id_fk foreign key (map_id) references maps(id)
);
