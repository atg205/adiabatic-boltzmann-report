INSTALLATION

Pas vraiment d'installation à faire, veillez :
- à avoir installé les fontes fira sans (https://tug.org/FontCatalogue/firasans/, incluses dans texlive normalement)
- à avoir les fichiers beamer[xxx].sty, default.beamer, toc.tex, merci.tex, sorbonne-[xxx].png dans le même 
  répertoire que vos créations
- de manière optionnelle, les fichiers liées à la biblio (library.bib et elsevier-vancouver.csl)

UTILISATION

- Soit directement avec un fichier latex (voir exemple_latex.tex). L'option par défaut est "style=medecine" (thème 
  rouge et logo "sorbonne université médecine". Vous pouvez aussi utiliser l'option "style=universite" pour obtenir
  un thème bleu et le logo "sorbonne université".
- Soit via rmarkdown (voir exemple_rmarkdown.Rmd, qui se compile directement avec le raccourcis Ctrl+Shift+K si vous 
  utilisez RStudio). Vous pouvez dans ce cas ajouter des packages et options spécifiques à latex dans le préambule. 
- La compilation fonctionne avec pdflatex ou xelatex. L'aspect des fonts ne sera pas exactement le même. Si vous 
  arrivez à faire fonctionner xelatex, il y a deux lignes à décommenter dans le préambule.