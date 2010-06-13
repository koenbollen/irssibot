
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

sub handle
{
	my $server = shift;
	my ($msg, $nick, $mask, $target ) = @_;

	# FIXME: find script dynamic:
	my $file = "$ENV{HOME}/.irssi/irssibot/irssibot.py";
	print $file;

	open( PY, "python \"$file\" \"$msg\" \"$nick\" \"$mask\" \"$target\" |" ) || die "Failed: $!\n";
	while( <PY> )
	{
		$_ =~ s/\s+$//;
		if( $_ =~ /^\// )
		{
			$server->command( $_ );
		}
		elsif( $_ =~ /^!/ )
		{
			if( $_ == "!prevent" )
			{
				Irssi::signal_stop();
			}
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
	print "handle: ( msg=$msg, nick=$nick, mask=$mask, target=$target )";
	handle( $server, $msg, $nick, $mask, $target );
}

Irssi::signal_add('message public', 'message');
Irssi::signal_add('message private', 'message');
Irssi::signal_add('message own_public', 'message');
