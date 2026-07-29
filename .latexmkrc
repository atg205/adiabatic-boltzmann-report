$pdf_mode = 1;
$out_dir = 'build';

# glossaries: rebuild .gls/.acr via makeglossaries when .glo/.acn change
add_cus_dep('glo', 'gls', 0, 'run_makeglossaries');
add_cus_dep('acn', 'acr', 0, 'run_makeglossaries');
sub run_makeglossaries {
    my ($base_name, $path) = fileparse($_[0]);
    pushd $path;
    my $ret = system "makeglossaries", $base_name;
    popd;
    return $ret;
}
push @generated_exts, 'glo', 'gls', 'glg', 'acn', 'acr', 'alg', 'ist';
