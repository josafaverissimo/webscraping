use hltv;

drop table if exists maps_picked;
drop table if exists maps_banned;
drop table if exists teams_results;
drop table if exists teams_maps_results;
drop table if exists matches;
drop table if exists events;

create table events(
    id int(11) unsigned not null primary key auto_increment,
    name varchar(255) not null,
    hltv_id int(11) unsigned not null
);

create table matches(
  id int(11) unsigned not null primary key auto_increment,
  hltv_id int(11) unsigned not null,
  event_id int(11) unsigned not null,
  matched_at timestamp,
  constraint matches_event_id_fk foreign key (event_id) references events(id)
);

create table matches_maps_picked(
    id int(11) unsigned not null primary key auto_increment,
    map_id int(11) unsigned not null,
    team_id int(11) unsigned not null,
    match_id int(11) unsigned not null,
    constraint maps_picked_map_id_fk foreign key (map_id) references maps(id),
    constraint maps_picked_team_id_fk foreign key (team_id) references teams(id),
    constraint maps_picked_match_id_fk foreign key (match_id) references matches(id)
);

create table matches_maps_banned(
    id int(11) unsigned not null primary key auto_increment,
    map_id int(11) unsigned not null,
    team_id int(11) unsigned not null,
    match_id int(11) unsigned not null,
    constraint maps_banned_map_id_fk foreign key (map_id) references maps(id),
    constraint maps_banned_team_id_fk foreign key (team_id) references teams(id),
    constraint maps_banned_match_id_fk foreign key (match_id) references matches(id)
);

create table matches_teams_results(
    id int(11) unsigned not null primary key auto_increment,
    team_id int(11) unsigned not null,
    result int(11) unsigned not null,
    match_id int(11) unsigned not null,
    constraint teams_results_team_id_fk foreign key (team_id) references teams(id),
    constraint teams_results_match_id_fk foreign key (match_id) references matches(id)
);

create table matches_teams_maps_results(
    id int(11) unsigned not null primary key auto_increment,
    team_id int(11) unsigned not null,
    rounds_played int(11) unsigned not null,
    ct_rounds_wins int(11) unsigned not null,
    tr_rounds_wins int(11) unsigned not null,
    constraint teams_maps_results_team_id_fk foreign key (team_id) references teams(id)
);
