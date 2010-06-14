
use strict;
use vars qw($VERSION %IRSSI);

use Irssi;

$VERSION = "1.0";
%IRSSI = (
	authors => "Koen Bollen",
	contact => "meneer\@koenbollen.nl",
	name => "irssibot",
	description => "wrapper to irssibot.py",
	license => 'GNU GPL v2 or later'
);

my $file = "/home/koen/.irssi/irssibot/irssibot.py";

sub execute
{
	my ($server, $cmd) = @{@_[0]};
	$server->command( $cmd );
}

sub handle
{
	my ($server, $msg, $nick, $mask, $target) = @{@_[0]};

	# FIXME: find script dynamic:
	my $file = "$ENV{HOME}/.irssi/irssibot/irssibot.py";

	$msg    =~ s/"/\\"/g;
	$nick   =~ s/"/\\"/g;
	$mask   =~ s/"/\\"/g;
	$target =~ s/"/\\"/g;
	open( PY, "python \"$file\" \"$msg\" \"$nick\" \"$mask\" \"$target\" |" ) || die "Failed: $!\n";
	while( <PY> )
	{
		$_ =~ s/\s+$//;
		if( $_ =~ /^\// )
		{
			Irssi::timeout_add_once( 100, \&execute, [$server, $_] );
		}
	}
	close( PY )
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
	Irssi::timeout_add_once( 10, \&handle, [$server, $msg, $nick, $mask, $target] );
}

Irssi::signal_add('message public', 'message');
Irssi::signal_add('message private', 'message');
Irssi::signal_add('message own_public', 'message');
