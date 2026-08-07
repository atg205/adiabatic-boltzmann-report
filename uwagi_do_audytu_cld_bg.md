# Ponowna ocena `audyt_cld_bg.md`

Ocena dotyczy **Revision 4** audytu z 7 sierpnia 2026 r. i bieżącego `report.tex`. Źródło raportu nie zmieniło się od commitu `5bc5a64`, natomiast HEAD całego repozytorium to obecnie `e2705c2`.

## Werdykt

Audyt jest teraz **w dużej mierze trafny, dobrze udokumentowany i bardzo użyteczny jako wewnętrzna kontrola jakości**. Jest znacznie lepszy od poprzedniej wersji: uczciwie wycofuje wcześniejszy nietrafiony zarzut wobec funkcji celu CEM, rozróżnia poprawki pełne i częściowe oraz wykrywa poważne sprzeczności w nowym eksperymencie czasu-do-progu.

Nie jest jednak jeszcze całkowicie wiarygodną recenzją końcową. Najważniejsze zastrzeżenia dotyczą nadmiernego uogólnienia wyniku `auto_scale`, niepoprawnej oceny reprodukowalności i zbyt pozytywnej oceny języka raportu.

| Kryterium | Ocena | Komentarz |
|---|---:|---|
| Trafność merytoryczna | **8/10** | Większość głównych ustaleń jest poprawna; jeden centralny wniosek o `beta_eff ≈ 2.8` jest uogólniony poza dane. |
| Jakość redakcyjna | **7,5/10** | Bardzo dobra identyfikowalność uwag, ale dokument jest gęsty, miejscami kategoryczny i miesza defekty naukowe z kosmetyką. |
| Praktyczna użyteczność | **9/10** | Lista napraw jest konkretna i prawie od razu wykonalna; wymaga zmiany kolejności priorytetów. |
| Gotowość jako formalna recenzja | **7/10** | Po korektach opisanych niżej może być solidną podstawą decyzji redakcyjnych. |

## Ustalenia audytu, które się potwierdzają

### 1. Poprawka rodziny referencyjnej CEM

Ocena F1 jest trafna. W linii 432 raport używa teraz właściwego widocznego rozkładu marginalnego rodziny z przeskalowaną pełną energią wspólną wartością `beta`:

```text
p_beta(v) ∝ exp(-beta a·v) Π_j 2 cosh(beta Theta_j).
```

To jest zgodne z energią RBM zapisaną w równaniu (13). Audyt prawidłowo odnotowuje również, że obecnych wartości RMSE nie można odtworzyć bez właściwego cache, checkpointów i skryptu eksperymentalnego.

### 2. Korekta wcześniejszego zarzutu wobec funkcji celu CEM

Sekcja M2 jest teraz merytorycznie znacznie lepsza. Audyt słusznie wycofuje twierdzenie, że funkcja celu oparta na zwykłych próbkach wspólnych jest z definicji źle określona. Pooled least squares może być zgodnym estymatorem; problemem pozostają wariancja, możliwa saturacja oraz brak porównania z wariantem warunkowym.

### 3. Mechanizm `auto_scale`

Sedno F2 jest poprawne: jeżeli `beta_x` jednolicie skaluje wszystkie współczynniki `h` i `J`, domyślne `auto_scale=True` usuwa ten wspólny mnożnik podczas dopasowania problemu do zakresu QPU. Potwierdza to [dokumentacja parametru `auto_scale`](https://docs.dwavequantum.com/en/latest/quantum_research/solver_parameters.html).

Odczyt Figure 9 przez audyt jest zgodny z wykresem: dla badanego przypadku `auto_scale=True` daje prawie płaskie `beta_eff ≈ 2.7–3.0`, a przy `False` wynik jest w przybliżeniu proporcjonalny do `1/beta_x` z mnożnikiem około 4,1.

### 4. Sprzeczność w wynikach sparsity

N1 jest prawdziwy. Linia 544 podaje zakres 8–17 razy, a linia 563 zakres 7–27 razy dla tego samego porównania. Cache wspiera pierwsze podsumowanie. To łatwy do naprawienia, jednoznaczny błąd.

Audyt trafnie rozpoznaje też, że wcześniejszy problem niematchowanych budżetów QPU przestał być błędem bieżącego tekstu nie dlatego, że wykonano poprawny eksperyment kontrolny, ale dlatego, że wycofano z raportu porównanie QPU–classical.

### 5. Problemy nowej Figure 7

Ustalenia N2, N3, N5 i N6 są zasadniczo poprawne:

- tekst mówi, że FPGA i VeloxQ osiągają ciasny próg w całym zakresie, choć przy `N=128` mają `0/20`;
- tekst mówi, że przy `N=128` żaden solver nie osiąga progu, choć LSB ma `4/20`;
- podpis definiuje pusty marker jako co najmniej jeden ocenzurowany seed, ale częściowo ocenzurowane punkty `19/20` i `12/20` są wypełnione;
- twierdzenie o przewadze około dwóch rzędów wielkości nie zachodzi przy największym `N`;
- tytuł mówi o TTS, podczas gdy mierzona jest inna metryka — TTE.

Audyt dobrze uznaje tę sekcję za najpoważniejszy problem nowego materiału.

### 6. Braki strukturalne raportu

Potwierdzają się brak abstraktu, Discussion/Conclusions, deklaracji dostępności danych i kodu, stabilnej daty oraz pełnego protokołu eksperymentalnego. Trafne są także uwagi o nieużytych w wynikach modelach LRTFIM i XXZ oraz o braku bezpośredniego testu dense-with-chains versus native-sparse.

### 7. Pozycjonowanie literaturowe

Audyt słusznie zawęża nowość projektu w świetle prac Kubo–Goto, Berns et al. i Chowdhury et al. Najbardziej obronnym wyróżnikiem pozostaje konkretny mechanizm integracji samplera i korekcji temperatury, a nie samo użycie maszyny Isinga, FPGA, rzadkiego RBM lub równoległych embeddingów.

## Najważniejsze korekty potrzebne w samym audycie

### 1. Nie wolno przenosić `beta_eff ≈ 2.8` na wszystkie wyniki QPU

To najważniejszy błąd audytu. Eksperyment z Figure 9 mierzy `beta_eff` dla jednego małego przypadku: `N=8`, jednego modelu, jednego solvera Pegasus i chain-free odwzorowania. Z tego wynika ogólna obserwacja, że przy jednolitym skalowaniu `beta_x` i włączonym `auto_scale` **`beta_x` nie steruje fizyczną skalą problemu**.

Nie wynika natomiast, że:

> every other QPU result sampled at beta_eff ≈ 2.8

Wartość efektywnej temperatury może zależeć od instancji, skali współczynników, solvera, embeddingu, łańcuchów, harmonogramu i freeze-out. Dokumentacja D-Wave wprost zastrzega, że złożone i osadzone problemy mogą zamarzać w innych punktach lub fragmentami: [freeze-out effective temperature](https://docs.dwavequantum.com/en/latest/ocean/api_ref_system/generated/dwave.system.temperatures.freezeout_effective_temperature.html). Wcześniejsza literatura również traktuje temperaturę jako zależną od instancji, np. [Benedetti et al.](https://arxiv.org/abs/1510.07611).

Audyt powinien napisać:

> Figure 9 pokazuje, że `beta_x` nie kontroluje temperatury przy `auto_scale=True` w badanej konfiguracji. Dla pozostałych eksperymentów QPU rzeczywiste `beta_eff` nie jest znane i wymaga osobnej kalibracji.

Z tego samego powodu rekomendacja „uruchomić wszystkie eksperymenty z `auto_scale=False` i `beta_x ≈ 4.1`” jest za mocna. Wartość około 4,1 nie musi przenosić się między solverami i instancjami; potrzebna jest kalibracja per klasa problemu albo jawne ograniczenie interpretacji.

### 2. Nowość wyniku `auto_scale` jest przeceniona

Stwierdzenie, że wynik jest samodzielnym, „genuine, citable calibration contribution” odpowiednim dla *Physical Review Applied*, jest opinią wydawniczą, a nie wynikiem audytu. Mechanizm usuwania wspólnego skalowania jest bezpośrednią konsekwencją udokumentowanej definicji `auto_scale`. Empiryczne pokazanie efektu na jednym RBM jest użyteczne, ale obecnie wygląda raczej jak ważna kontrola metodologiczna lub case study niż wykazana nowość naukowa.

Bez szerszego przeglądu literatury i testów na wielu instancjach, solverach oraz embeddingach bezpieczniejsze sformułowanie brzmi:

> Wynik autoskalowania jest praktycznie użyteczną kontrolą i może stanowić element wkładu pracy, lecz jego samodzielna nowość i generalność nie zostały jeszcze wykazane.

### 3. Sekcja o reprodukowalności zawiera fałszywie pozytywne stwierdzenie

Audyt twierdzi, że cache exact floor i „both of Figure 14's plotting scripts are now committed”. W bieżącym repozytorium są cache i gotowe PDF/PNG, ale **nie ma skryptów generujących wykres sparsity**. Nazwane później pliki `plot_sparsity_ablation_floor.py` i `exact_ansatz_floor.py` nie występują również w lokalnym checkoutcie repozytorium implementacyjnego.

Dodatkowo:

- dla Figure 7 są wyłącznie dwa pliki PDF; brak surowych danych, cache i skryptu;
- dla walidacji CEM nadal brakuje właściwego eksperymentu, checkpointów i cache;
- dla Figure 9 istnieje `scripts/dtv_autoscale.py`, ale w obecnym położeniu nie jest samodzielnie uruchamialnym artefaktem: zachował ścieżkę użycia `scripts/dtv/dtv_autoscale.py`, wylicza `_ROOT` o jeden poziom za wysoko i importuje kod z repozytorium, którego nie ma w tym projekcie; brak też wynikowego JSON i checkpointu;
- nie ma opisu środowiska ani kompletnego protokołu odtworzenia nowych eksperymentów.

Wobec tego ocena `C−` jest optymistyczna. Bardziej adekwatne byłoby **D+ lub C− z wyraźnym zaznaczeniem, że żadnego z trzech nowych headline experiments nie da się obecnie odtworzyć end-to-end**.

### 4. „Language is genuinely clean” jest nieprawdziwe

Audyt utożsamia brak literówek ze zdrowym językiem. Raport nadal zawiera widoczne błędy gramatyczne i niezręczności, m.in.:

- `the D-Wave's ability` i `The D-Wave's Quantum Annealers performance`;
- `a initial driver Hamiltonian`;
- `a handful of highly probable sample configuration`;
- `In this chapter, we are going to describe...` w artykule;
- `Lanczos algorithm ... only returns the matrix' lowest eigenvalue`;
- `For budget constraints`;
- niepoprawną składnię zdania celu pracy w linii 51.

Werdykt powinien brzmieć raczej: **„spelling substantially improved; a professional English-language edit is still required.”**

### 5. Priorytety P0 są źle ustawione

N1 nie jest „Highest-priority fix in the document”. To prosta sprzeczność w jednym zakresie liczbowym. Znacznie ważniejsze są:

1. brak danych i metodologia Figure 7;
2. fałszywe zdania opisujące Figure 7 oraz błędny podpis markerów;
3. nieznana podstawa pomiaru wall-clock i obsługa cenzorowania;
4. nadinterpretacja pozostałych wyników QPU po wykryciu działania `auto_scale`;
5. dopiero potem zakres 8–17× versus 7–27×.

Audyt sam w Summary nazywa Figure 7 blokadą, ale jego kolejność P0 temu przeczy.

### 6. Audyt za słabo kwestionuje metodologię porównania TTE

Stwierdzenie, że siedem solverów porównano przy „matched hyperparameters”, nie wystarcza do uczciwego benchmarku. Identyczna liczba próbek i iteracji nie oznacza porównywalnego wysiłku dla MCMC, SA, LSB, FPGA i QPU; część metod może być nastrojona, a VeloxQ jest jawnie opisany jako `untuned`.

Brakuje co najmniej:

- surowych czasów i trajektorii dla wszystkich seedów;
- definicji długości rolling average;
- dokładnego kryterium „drops below and stays there”;
- informacji, czy czas QPU obejmuje programming, embedding, queueing, network, readout i postprocessing;
- definicji timeoutu i sposobu wyznaczania punktu `censored (extrapolated)`;
- statystycznej procedury dla median przy cenzorowaniu;
- strojenia solver-specific lub uzasadnienia wspólnego protokołu.

Audyt zauważa część tych problemów, lecz powinien jasno stwierdzić, że obecny wykres nie uzasadnia porównania wydajności solverów, nawet po poprawieniu dwóch zdań i markerów.

### 7. Drobne nieścisłości audytu

- Nagłówek każe potwierdzić target komendą `git log --oneline -1`, lecz ta zwraca obecnie `e2705c2`, nie `5bc5a64`. Poprawna kontrola to `git log -1 -- report.tex` albo porównanie hasha pliku.
- W N2 zapis „LSB is drawn solid with 4/20” jest mylący: linia LSB jest przerywana, a **marker** jest wypełniony. Sedno zarzutu pozostaje prawdziwe.
- „Figure 7 cannot be decoded” jest retorycznie zbyt absolutne. Lepsze: „caption and markers are inconsistent, so censoring cannot be interpreted unambiguously”.
- Lokalny checkout implementacji rzeczywiście jest 69 commitów za `origin/main`, ale jest to stan względem lokalnego refa śledzącego; bez `git fetch` nie wiadomo, czy zdalny stan nadal jest dokładnie taki sam.
- N14 łączy w jednym akapicie błędy istotne, styl, LaTeX i czysto kosmetyczne różnice. Utrudnia to ustalenie priorytetów.

## Ocena stylu audytu

### Mocne strony

- bardzo dobra identyfikowalność przez linie, równania, pliki i artefakty;
- jawne etykiety poziomu pewności;
- wyraźne rozróżnienie: fixed, partially fixed, obsolete i not fixed;
- uczciwa autokorekta wcześniejszego błędu M2;
- konkretne minimalne naprawy;
- dobre uchwycenie sprzeczności między tekstem a wykresami;
- rozdzielenie correctness, completeness, novelty, readability i reproducibility.

### Słabe strony

- zbyt wiele szczegółów niskiego priorytetu w głównym toku;
- kilka opinii o szansach publikacyjnych jest przedstawionych niemal jak fakt;
- pojedyncze kalibracje bywają uogólniane na cały raport;
- Summary jest miejscami bardziej kategoryczne niż późniejsze zastrzeżenia;
- istotne braki reprodukowalności nowej Figure 7 zostały przeoczone;
- „24 new defects” brzmi efektownie, ale zlicza razem problemy naukowe i kosmetyczne.

Lepsza konstrukcja audytu to krótka lista 5–7 blokad w tekście głównym, a pełna lista kosmetyki, logów i mikrospójności w dodatku.

## Zalecana kolejność poprawek audytu

1. Usunąć wszystkie uogólnienia, że pozostałe eksperymenty QPU miały `beta_eff ≈ 2.8`; pozostawić jedynie wniosek o nieskuteczności `beta_x` przy `auto_scale=True`.
2. Przepisać sekcję Reproducibility: dodać brak danych/skryptu Figure 7, brak skryptów sparsity oraz niesamodzielność `dtv_autoscale.py`.
3. Zmienić ocenę języka z „genuinely clean” na „bez wykrytych literówek, lecz nadal wymagający redakcji językowej”.
4. Ustawić Figure 7 i metodologię TTE przed N1 w P0.
5. Osłabić twierdzenie o nowości i potencjale publikacyjnym wyniku autoskalowania.
6. Dodać krytykę porównywalności solverów oraz pełną listę braków definicji TTE.
7. Poprawić komendę identyfikującą target, sformułowanie o markerze LSB i kilka zdań absolutnych.

## Konkluzja

`audyt_cld_bg.md` jest **bardzo dobrym audytem roboczym** i trafnie wykrywa większość najważniejszych problemów obecnej wersji raportu. Najcenniejsze są ustalenia o Figure 7, rodzajach CEM, `auto_scale`, sprzeczności w sparsity oraz brakach strukturalnych.

Przed potraktowaniem go jako formalnej recenzji trzeba jednak skorygować jego własny centralny skrót myślowy: **z jednego pomiaru `beta_eff ≈ 2.8` nie wynika taka sama temperatura we wszystkich eksperymentach QPU**. Trzeba też uczciwie obniżyć ocenę reprodukowalności i jakości językowej. Po tych zmianach audyt będzie trafny, dobrze napisany i merytorycznie bardzo pomocny.
