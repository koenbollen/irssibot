
use strict;
use vars qw($VERSION %IRSSI);

use Irssi;

my $allow = 1;

$VERSION = "1.0";
%IRSSI = (
	authors => "Koen Bollen",
	contact => "meneer\@koenbollen.nl",
	name => "irssibot",
	description => "wrapper to irssibot.py",
	license => 'GNU GPL v2 or later'
);

sub execute
{
	my ($server, $cmd) = @{@_[0]};
	# TODO: Add whitelist.
	$server->command( $cmd );
}

sub sanatize
{
	my $data = shift;
	$data =~ s/\\/\\\\/g;
	$data =~ s/"/\\"/g;
	$data =~ s/\`/\\\`/g;
	$data =~ s/\$/\\\$/g;
	return $data;
}

sub handle
{
	my ($server, $msg, $nick, $mask, $target) = @{@_[0]};

	# FIXME: find script dynamic:
	my $file = "$ENV{HOME}/.irssi/irssibot/irssibot.py";

	$msg    = sanatize( $msg );
	$nick   = sanatize( $nick);
	$mask   = sanatize( $mask );
	$target = sanatize( $target );
	open( PY, "python \"$file\" \"$msg\" \"$nick\" \"$mask\" \"$target\" |" ) || die "Failed: $!\n";
	while( <PY> )
	{
		$_ =~ s/\s+$//;
		if( $_ =~ /^\// )
		{
			Irssi::timeout_add_once( 100, \&execute, [$server, $_] );

			# A plugin issued a command, triggering flood control:
			my $flood;
			$flood = Irssi::settings_get_int( "irssibot_flood" );
			$flood = 1000 if $flood < 10;
			$allow = 0;
			Irssi::timeout_add_once( $flood, \&overflow_timeout, undef );
		}
	}
	close( PY )
}

sub overflow_timeout
{
	$allow = 1;
}

sub message
{
	my ($msg, $nick, $mask, $target);
	my $server = shift;
	my $length = @_;
	if( $length == 4 )
	{
		($msg, $nick, $mask, $target) = @_;
	}
	elsif( $length == 3 )
	{
		($msg, $nick, $mask) = @_;
	}
	elsif( $length == 2 )
	{
		($msg, $target) = @_;
	}

	if( $allow )
	{
		Irssi::timeout_add_once( 10, \&handle, [$server, $msg, $nick, $mask, $target] );
	}
}

Irssi::settings_add_int( "irssibot", "irssibot_flood", 1000 );
Irssi::signal_add('message public', 'message');
Irssi::signal_add('message private', 'message');
Irssi::signal_add('message own_public', 'message');
