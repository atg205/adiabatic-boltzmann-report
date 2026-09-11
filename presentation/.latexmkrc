$pdf_mode = 1; # pdflatex -> pdf
$out_dir = 'build';
$ENV{'TEXINPUTS'} = './example_theme//:' . ($ENV{'TEXINPUTS'} // '');
$ENV{'BIBINPUTS'} = './example_theme:' . ($ENV{'BIBINPUTS'} // '');
$ENV{'BSTINPUTS'} = './example_theme:' . ($ENV{'BSTINPUTS'} // '');
