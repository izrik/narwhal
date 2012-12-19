#!/usr/bin/perl

use strict;
use LWP::Simple;
use XML::LibXML;
use Getopt::Long;
use File::Spec;
use File::Copy;
use File::Basename;

my $root = dirname(__FILE__);

my $no_restart_tomcat = '';
my $help = '';
my %params = ();

GetOptions(
  'no-restart-tomcat' => \$no_restart_tomcat,
  'help' => \$help,
  'param=s' => \%params,
  );

sub get_config_sets {

  opendir DIR, "$root/configs" or die "Can't open directory \"$root/configs\": $!";

  my @config_sets = ();

  for my $f (readdir DIR) {
    next if (not -d "$root/configs/$f");
    next if ($f eq '.' or $f eq '..');
    next if (not -e "$root/configs/$f/.config-set.xml");
    push @config_sets, $f;
  }

  close DIR;

  return sort @config_sets;
}

sub print_usage {

  print STDERR "Usage:\n";
  print STDERR "  $0 [options] <config-set>\n";
#  print STDERR "  $0 [options] <config-set URI>\n";
  print STDERR "\n";
  print STDERR "  config-set:                The name of the config set to apply\n";
  print STDERR "\n";
  print STDERR "  options:\n";
  print STDERR "    --help,                  This text\n";
  print STDERR "    --no-restart-tomcat      Don't shut down Tomcat before copying config files, and don't start Tomcat after copying the files\n";
  print STDERR "    --param <name>=<value>   Set a config parameter with name <name> to <value>\n";
  print STDERR "\n";
  print STDERR "The available config-sets are:\n";
  print STDERR (map { "  $_\n" } get_config_sets());
  print STDERR "\n";
}

sub print_tree {
  my $ref = shift || die "print_tree";
  my $indent = shift || '';

  if (not ref $ref) {
    print "$indent = $ref\n";
  } elsif (ref $ref eq 'ARRAY') {
    my $i = 0;
    for my $elem (@$ref) {
      print_tree($elem, "$indent\[$i]");
      $i++;
    }
  } elsif (ref $ref eq 'HASH') { 
    for my $key (keys %$ref) {
      print_tree($ref->{$key}, "$indent\{$key}");
    }
  } elsif (ref $ref eq 'REF') { 
    print_tree($$ref, "$indent\$");
  } else { 
    die "Unknown ref \"$ref\" (".(ref $ref).")";
  }

}

my $config = shift @ARGV;

if (not $config or $help) {
  print_usage();
  exit;
}

my $configset = '';
my $context = '';

#if ($config =~ /^[\w-]+\:/) {
#
#  # uri
#  die "Not Implemented";
#
#  $configset = get $config;
#
#} els

if ($config =~ /^[\w-]+$/) { 

  # named config set
  if (not -d "$root/configs/$config") { 
    print STDERR "No config-set named \"$config\".\n"; 
    print STDERR "\n";
    print STDERR "The available config-sets are:\n";
    print STDERR (map { "  $_\n" } get_config_sets());
    print STDERR "\n";
    exit;
  }

  $context = "$root/configs/$config";
  $configset = XML::LibXML->load_xml( location => "$context/.config-set.xml" );

} else { 

  die "Invalid config-set descriptor \"$config\". Descriptor should be either a named config-set name or a URI to a config-set xml specification."

}

# parse the xml file using some library

# run through the <folder> element
  # for each <file> element, copy the file specified by 'src' attribute to the file specified by 'dest' attribute. if no 'dest' given, use 'src'.

# NOTE: this doesn't allow src to be a URI

sub copy_and_apply_params {

  my $src_filename = shift or die "No source filename given";
  my $dest_filename = shift or die "No destination filename given";
  my %params = @_;

  open FILE, $src_filename or die "Can't open \"$src_filename\": $!";
  my $content = join'',(<FILE>);
  close FILE;

  open FILE, ">$dest_filename" or die "Can't open \"$dest_filename\": $!";
  $content =~ s/\$\{([\w\d\-\_\.]+)\}/if (exists $params{$1}) { $params{$1} } else { warn "Warning: parameter \"$1\" not substituted"; "\$\{$1\}" }/eg;
  print FILE $content;
  close FILE;

}

sub process_doc {
  my $doc = shift;
  my @paths = ();

  my @n = $doc->findnodes( 'folder' );
  my $n = scalar(@n);
  print "$n folder nodes.\n";
  for my $folder ( $doc->findnodes( 'folder' ) ) {
    my $path = $folder->findnodes( '@path' ) or die "No path given";
    print "folder: $path\n";
    push @paths, $path;
    $path = File::Spec->catdir( @paths );

    for my $file ( $folder->findnodes('file')) {
      
      my $src = ($file->findvalue('@src'));
      my $dest = ($file->findvalue('@dest')) || $src;
      
      my $src2 = File::Spec->catfile($context, $src);
      my $dest2 = File::Spec->catfile($path, $dest);

      print "Copy from \"$src2\" to \"$dest2\"";
      if (keys %params > 0) { print ", applying config parameters"; }
      print "\n";
      copy_and_apply_params($src2, $dest2, %params);
      #copy($src2, $dest2) or die "ERROR: $!";

    }
    pop @paths;
  }
}

print "Configuring for \"$config\" config-set\n";

if (not $no_restart_tomcat) {
  print `service tomcat7 stop`;
}

process_doc($configset->documentElement());

if (not $no_restart_tomcat) {
  print `service tomcat7 start`;
}




