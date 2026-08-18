# Druga runda oceny `audyt_cld_bg.md`

**Oceniana wersja:** Revision 9, commit raportu `4606b1a`; implementacja `iitis/adiabatic-boltzmann` przypięta przez audyt do `a4b0f2006`.

**Ocena ogólna: 8,2/10.** Revision 9 jest wyraźnie lepsza od Revision 8: uczciwie wycofuje fałszywy blocker `auto_scale`, prawidłowo rozszerza zakres o repozytorium implementacji, naprawia analizę energii i lepiej kalibruje część oznaczeń pewności. Nadal nie jest jednak całkowicie gotowa jako formalna recenzja. Najważniejszy pozostający problem to zbyt mocna przyczynowa teza B1, błędny opis granicy pomiaru czasu w B2 oraz przeoczona rozbieżność między opisem i implementacją walidacji zbieżności.

## Najważniejsze ustalenia drugiej rundy

### 1. B2 zachowuje trafną konkluzję, ale opiera ją na błędnym opisie klasycznego zegara

Audyt twierdzi, że klasyczne serie zawierają pełny koszt obliczeń host-side SR, w tym lokalne energie, obserwable gradientowe i CG, podczas gdy QPU raportuje tylko `qpu_access_time`.

Przypięta implementacja pokazuje coś innego. `Trainer` uruchamia zegar bezpośrednio przed `sampler.sample(...)`, zatrzymuje go bezpośrednio po tym wywołaniu i dopiero później oblicza lokalne energie, gradienty oraz rozwiązuje układ SR/CG. Komentarz w kodzie mówi również jawnie, że pomiar energii obejmuje tylko wywołania samplera, a SR/CG jest wyłączone:

- [`src/encoder.py`, inicjalizacja pomiaru](https://github.com/iitis/adiabatic-boltzmann/blob/a4b0f2006cf0b5bf3a7ae40cea70093a5fab9d41/src/encoder.py#L332-L359),
- [`src/encoder.py`, granice zegara](https://github.com/iitis/adiabatic-boltzmann/blob/a4b0f2006cf0b5bf3a7ae40cea70093a5fab9d41/src/encoder.py#L460-L567).

Wniosek audytu pozostaje częściowo słuszny: `qpu_access_time` i czas ścienny klasycznego wywołania samplera mają różne granice systemowe i nie powinny być bez wyjaśnienia nazywane bezpośrednio porównywalnym wall-clock TTE. Nie jest jednak prawdą, że tylko QPU ma wyzerowany koszt SR. W rzeczywistości wykres przedstawia przede wszystkim **sampler time to validated convergence**, nie pełny czas treningu dla żadnej serii.

Ten sam problem dotyczy interpretacji energii: zmierzono energię GPU podczas samplingu, a nie pełną energię potrzebną do osiągnięcia zbieżności całego algorytmu.

### 2. B1 wykazuje rzeczywisty bias rozmiarowy, ale nie dowodzi, że obserwowane skalowanie jest artefaktem

Pomiar `CV·sqrt(N)` na stanach próbnych dla `N=8,10,12` jest wartościowy i pokazuje, że stały próg CV nie ma tej samej trudności przy różnych rozmiarach. Audyt prawidłowo oznacza ekstrapolowany czynnik około 2,8 jako `inference`.

Nie wykonano jednak testu rozstrzygającego: ponownego przeliczenia rzeczywistych historii QPU i FPGA z kryterium `CV·sqrt(N) < const` albo z bezpośrednim oracle-based przekroczeniem błędu energii. Bez tego nie można stwierdzić, że ujemne wykładniki QPU **są artefaktem**. Można stwierdzić, że są **silnie skonfundowane przez zależne od N kryterium zatrzymania** i nie uzasadniają obecnego twierdzenia o skalowaniu.

B1 powinno więc zostać przemianowane na przykład na: „The headline scaling claim is confounded by a size-dependent stopping rule”. Status przyczynowy powinien pozostać `inference` do czasu ponownej analizy faktycznych przebiegów.

### 3. Revision 9 przeoczyła błąd okna walidacyjnego w przypiętym generatorze

`compute_convergence_iter(...)` zwraca koniec pierwszego ciągu 10 iteracji spełniających próg CV. Następnie `compute_validated_convergence_iter(...)` wyznacza:

```python
plateau = energies[conv_iter - 1 : conv_iter - 1 + window]
```

To nie są iteracje, które uruchomiły detektor. Dla `window=10` powinno to być zasadniczo okno kończące się w `conv_iter`, czyli `energies[conv_iter-window:conv_iter]`. Obecny kod bierze punkt końcowy oraz do dziewięciu **przyszłych** iteracji. Przy zbieżności wykrytej w ostatniej iteracji walidacja opiera się tylko na jednym punkcie.

Źródło: [`paper_figures.py`, funkcje zbieżności](https://github.com/iitis/adiabatic-boltzmann/blob/a4b0f2006cf0b5bf3a7ae40cea70093a5fab9d41/scripts/viz/paper_figures.py#L57-L110).

Jest to istotna rozbieżność z `report.tex`, który mówi o energii uśrednionej „over that self-detected plateau”. Może ona zmieniać status walidacji, liczby `n/20`, mediany, wykładniki skalowania i wykres energii. Przed dalszą interpretacją B1/B2/B8 należy poprawić indeksowanie i przeliczyć figury.

### 4. B8 dowodzi nieujawnionej analizy progów, ale nie dowodzi post-selekcji

W przypiętym repozytorium faktycznie znajdują się warianty dla `CV ∈ {0.03, 0.05}` i `epsilon ∈ {0.01, 0.1}`, a raport pokazuje najluźniejszą parę. To ważne i powinno zostać ujawnione wraz z analizą wrażliwości.

Samo istnienie kilku wygenerowanych plików nie dowodzi jednak zdania Revision 9, że para „was chosen after seeing the alternatives”. Warianty mogły być analizą odporności, etapami rozwoju figury albo wynikiem wcześniej określonego wyboru. Aby podnieść ten punkt do zarzutu o selektywnym raportowaniu, potrzebny jest commit history, notatka eksperymentalna albo wykazanie, że wniosek zmienia się pomiędzy wariantami.

Najlepsza poprawka audytu: nazwać B8 „undisclosed threshold sensitivity analysis”, zestawić dla wszystkich czterech par liczby sukcesów, mediany i wykładniki, a dopiero potem ocenić, czy główny wynik jest odporny.

### 5. Przypięty generator nie odtwarza dokładnie figury użytej w manuskrypcie

Audyt zauważa jedynie usunięcie sufiksu parametrów z nazwy pliku. Problem jest większy:

- `figures/fig10c_tte_vs_n_self_convergence.pdf` w repozytorium raportu ma SHA-256 `4a56be72636ecb8bdc51654ec591b14f99fdf83a36e4f3af2ae32b940d5cd74c`;
- odpowiadający mu wariant upstream `fig10c_tte_vs_n_self_convergence_cv0.05_eps0.1.pdf` ma SHA-256 `ded0bc9456776e085147371064496331e5b80aa3bbfdbf2b15841887ede6a5a0`;
- figura raportu zawiera dopasowane wykładniki `∝ N^p` w legendzie, podczas gdy figura i funkcja przy przypiętym commicie ich nie zawierają;
- blok `__main__` przypiętego `paper_figures.py` nie wywołuje generatorów fig10c/fig10d.

Nie jest to więc wyłącznie zmiana nazwy. Dokładna figura raportu pochodzi z innego albo niecommittowanego stanu kodu. Ocena reprodukowalności B− jest możliwa dla ogólnego eksperymentu, lecz **nie dla dokładnego artefaktu publikacyjnego** bez wskazania właściwego commita lub skryptu.

### 6. Liczba „69 commitów podczas audytu” jest niepoprawna

GitHub compare pokazuje:

- `4746ef128...a4b0f2006`: 13 commitów;
- lokalny stary checkout `2383dacff...a4b0f2006`: 82 commity, od 16 czerwca do 17 sierpnia 2026 r.

Liczba 69 pochodzi ze starszego pomiaru opóźnienia lokalnego checkoutu i nie oznacza, że repozytorium przesunęło się o 69 commitów „during this audit alone”. M12 powinno używać 13 commitów między przypiętymi stanami albo po prostu stwierdzać, że nieprzypięty URL jest niestabilny.

### 7. M9 łączy dwa różne benchmarki zbyt mocnym językiem

Nie ma logicznej sprzeczności pomiędzy tym, że QPU przegrywa w pokazanych wcześniej benchmarkach TTS dla rotacji/faktoryzacji, a możliwością korzystniejszego skalowania w późniejszym benchmarku TTE dla RBM-VMC. Są to inne problemy, metryki i protokoły.

Pozostałe części M9 są trafne: podpis panelu (b) nadmiernie uogólnia przewagę losowania, zdanie o dominacji dopiero dla `N ≳ 100` nie odpowiada całemu panelowi (a), a digitisation danych panelu (a) powinna być ujawniona. Pierwsze zdanie M9 należy jednak zmienić z „argues the opposite direction to the abstract” na informację, że pozornie odmienne trendy wymagają jawnego rozdzielenia zakresów i metryk.

### 8. Drobniejsze korekty języka audytu

- „withheld experiment” w B5 sugeruje intencjonalne zatajenie, którego same pliki nie dowodzą; bezpieczniej: „unreported QPU arm”.
- Nagłówek M14 „Three defects print on every page” jest dosłownie nieprawdziwy: listingi i podwójny label nie pojawiają się na każdej stronie. Powinno być „Three defects visible in the rendered PDF”.
- Komenda usuwania danych wrażliwych powinna zostać przedstawiona jako procedura wymagająca kopii bezpieczeństwa, sprawdzenia wszystkich refs/tags i ponownego ustawienia remote, ponieważ `git filter-repo` zwykle usuwa `origin` jako zabezpieczenie.

## Co Revision 9 poprawiła bardzo dobrze

- Jawnie przyznaje i wycofuje błędy Revision 8 zamiast maskować je zmianą numeracji.
- Przypina repozytorium implementacji i podnosi ocenę reprodukowalności na podstawie rzeczywistych artefaktów.
- Poprawnie przeformułowuje problem energii: nie istnieje wynik QPU, więc abstrakt nie może deklarować przewagi nad QPU w tej metryce.
- Rozdziela fakty od inferencji znacznie lepiej niż Revision 8.
- B3, B4, rdzeń B5, B6 i B7 pozostają mocne i dobrze udokumentowane.
- M1, M2, M3, M6, M8, M15 i M16 są praktyczne oraz istotne dla poprawy raportu.
- Nowa kolejność P0 właściwie stawia metodologię zegara i cenzorowania przed kosmetyką.
- Wskazanie istniejącej figury `marshall_comparison.pdf` zamienia krytykę w niemal natychmiastową poprawkę manuskryptu.

## Oceny cząstkowe Revision 9

| Kryterium | Ocena |
|---|---:|
| Trafność głównych problemów manuskryptu | 8,5/10 |
| Aktualność i pinning materiału | 9/10 |
| Rzetelność oznaczeń pewności | 7,5/10 |
| Analiza reprodukowalności | 7,5/10 |
| Struktura i priorytety | 9/10 |
| Styl i precyzja języka | 8/10 |
| Gotowość jako formalna recenzja | 8/10 |

## Zalecana Revision 10

1. Poprawić B2: obie strony wykluczają SR/CG; problemem są różne granice samplera oraz błędna etykieta pełnego wall-clock TTE.
2. Zmienić B1 z dowiedzionego „artefaktu” na silne skonfundowanie i przeliczyć rzeczywiste historie z kryterium niezależnym od N.
3. Dodać blocker dotyczący błędnego, patrzącego w przyszłość okna `plateau` i ponownie wygenerować wszystkie liczby zależne od walidacji.
4. Przeformułować B8 bez nieudowodnionego zarzutu post-selekcji; pokazać tabelę wrażliwości dla wszystkich progów.
5. Przypiąć dokładny kod generujący figurę z wykładnikami albo usunąć rozbieżność między artefaktem raportu i upstream.
6. Poprawić liczbę commitów w M12 oraz język M9, B5 i M14.
7. Po regeneracji ponownie sprawdzić B3, B4, M1 oraz wszystkie `n/20`, ponieważ zależą od błędnie wyciętego okna walidacyjnego.

## Werdykt końcowy

Revision 9 jest już mocnym audytem roboczym i dużym krokiem naprzód względem Revision 8. Najważniejsze problemy raportu zostały rozpoznane trafnie, a proces korekty jest przejrzysty. Nie należy jednak jeszcze nazywać jej wersją końcową: jeden z centralnych blockerów ma zbyt silną tezę przyczynową, drugi błędnie opisuje mierzony czas, a kod użyty do walidacji zawiera przeoczone przesunięcie okna, które może zmienić główne liczby benchmarku.

Po wykonaniu Revision 10 i ponownym wygenerowaniu figur audyt powinien osiągnąć około **9–9,5/10**.
