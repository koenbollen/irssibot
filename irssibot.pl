
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
	my ($ref) = @_;
	my ($server, $cmd) = @{$ref};
	$server->command( $cmd );
}

sub handle
{
	my $server = shift;
	my ($msg, $nick, $mask, $target ) = @_;

	# FIXME: find script dynamic:
	my $file = "$ENV{HOME}/.irssi/irssibot/irssibot.py";

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
	handle( $server, $msg, $nick, $mask, $target );
}

Irssi::signal_add('message public', 'message');
Irssi::signal_add('message private', 'message');
Irssi::signal_add('message own_public', 'message');
