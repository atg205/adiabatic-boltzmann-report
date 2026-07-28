# Uwagi do `audyt_cld_bg.md`

## Ocena ogólna

Audyt jest w dużej mierze trafny i bardzo pomocny, ale nie powinien być przyjęty bez korekt jako ostateczna recenzja naukowa.

| Kryterium | Ocena |
|---|---:|
| Trafność merytoryczna | **8/10** |
| Jakość redakcyjna | **6,5/10** |
| Praktyczna użyteczność | **8,5/10** |

Największą wartością dokumentu są: przypięcie ustaleń do konkretnego commitu, sprawdzalne odwołania do linii i artefaktów kompilacji, wykrycie problemu z walidacją CEM, analiza budżetów eksperymentu QPU oraz uporządkowane rekomendacje P0/P1. Jednocześnie kilka wniosków jest sformułowanych zbyt kategorycznie, część propozycji napraw jest nieprecyzyjna, a przegląd literatury nie jest kompletny.

## Ustalenia, które są dobrze uzasadnione

### 1. Pochodzenie i metryka dokumentu

Dane w nagłówku audytu są poprawne dla commitu `973f11b`: `report.tex` ma 712 linii, skompilowany raport 21 stron, źródło zawiera 33 środowiska `equation`, 13 figur i 15 pozycji bibliograficznych, z których 12 jest cytowanych.

### 2. Niewłaściwa rodzina referencyjna w walidacji CEM

Sedno zarzutu C1 jest poprawne. Skalowanie pełnej energii RBM prowadzi do marginalnego rozkładu

```text
p_β(v) ∝ exp(−β a·v) ∏_j 2 cosh(β Θ_j),
```

a nie do rodziny

```text
|Ψ(v)|^(2β) ∝ exp(−β a·v) ∏_j [2 cosh(Θ_j)]^β.
```

Rodziny te są identyczne dla `β=1`, ale na ogół różnią się poza tym punktem. Oryginalna praca Kubo i Goto definiuje temperaturę względem pełnego rozkładu Boltzmanna `B_β(s)`, a CEM porównuje z warunkowymi wartościami oczekiwanymi:

- https://arxiv.org/html/2512.02323v1

Oznacza to, że liczby RMSE w raporcie nie mogą być interpretowane jako czysty błąd estymatora CEM, dopóki walidacja nie zostanie powtórzona względem właściwej rodziny.

### 3. Niespójność znaku CEM

Przy energii zapisanej w raporcie jako

```text
E(v,h) = a·v + b·h + h·W·v
```

i rozkładzie `p ∝ exp(−βE)` zachodzi

```text
E[h_j | v] = −tanh(β Θ_j),
```

a nie `+tanh(β Θ_j)`. Audyt trafnie identyfikuje wewnętrzną niespójność konwencji. Nie dowodzi to jednak automatycznie, że kod ma ten sam błąd — w repozytorium nie ma implementacji pozwalającej to sprawdzić.

### 4. `auto_scale`

Podstawowy zarzut jest zasadny. D-Wave skaluje współczynniki problemu tak, aby wykorzystać dostępny zakres sprzętowy. Jednorodne przemnożenie wszystkich wag jest zatem zasadniczo kompensowane przez `auto_scale`, co podważa opis kontroli temperatury poprzez wspólny współczynnik `β_x`.

Dokumentacja:

- https://docs.dwavequantum.com/en/latest/quantum_research/solver_parameters.html

### 5. Niematchowane budżety eksperymentu sparsity

Zawartość cache potwierdza ustalenie C4:

- klasyczna część eksperymentu ma po 300 iteracji SR dla każdego poziomu i seeda;
- część QPU ma od 14 do 300 iteracji;
- dla największej rzadkości liczby iteracji wynoszą `44, 25, 18, 14, 32`, czyli średnio 26,6.

W tej sytuacji nie można oddzielić wpływu sprzętu od około dziesięciokrotnie mniejszego budżetu treningowego. To jeden z najważniejszych i najlepiej udokumentowanych punktów audytu.

### 6. Błędy redakcyjne i LaTeX

Potwierdzone są m.in.:

- błędne równanie problemowego Hamiltonianu w linii 144;
- błędne odwołanie do `anneal_schedule` zamiast figury z `D_TV`;
- źle umieszczone etykiety sekcji i podfigury;
- błędna definicja RBM mówiąca o braku połączeń między warstwami zamiast wewnątrz warstw;
- niezbilansowany nawias w równaniu (20);
- błędy makr miesięcy w BibTeX;
- błąd nazwiska `Pawłłowski`;
- brak abstraktu i sekcji Conclusions/Discussion;
- brak warunków brzegowych przy TFIM;
- niespójne użycie `S` i `S+λI` w dodatku;
- niepoprawna etykieta osi Fig. 12.

### 7. Niekompletność wyników

Audyt słusznie wskazuje brak:

- pomiaru `D_TV` dla próbek z QPU;
- porównania czasu QPU z metodami klasycznymi;
- pełnego zestawu hiperparametrów;
- jasnej liczby dokładności treningu prowadzonego próbkami z QPU;
- testu hipotezy „native sparse RBM vs dense embedded RBM”;
- sekcji podsumowującej wyniki;
- deklaracji dostępności kodu i danych.

### 8. Pozycjonowanie parallel embeddings i sparse Boltzmann machines

Stwierdzenie, że parallel embeddings nie są nowym wkładem, jest dobrze uzasadnione. Bezpośrednim wcześniejszym przykładem jest:

- E. Pelofske, G. Hahn, H. N. Djidjev, *Parallel quantum annealing*, Scientific Reports 12, 4499 (2022): https://www.nature.com/articles/s41598-022-08394-8

Istnieje także wcześniejsza praca o natywnie rzadkiej maszynie Boltzmanna na D-Wave:

- J. Park et al., *Benchmarking the D-Wave Quantum Annealer as a Sparse Boltzmann Machine: Recognition and Timing Performances*, UCNC 2024.

## Punkty wymagające korekty w audycie

### 1. C1: „mismatch alone explains the entire RMSE”

To sformułowanie jest zbyt mocne. Matematyczna niezgodność rodzin jest pewna, ale testy opisane jako „run A/B” wykorzystują inne losowe wagi niż właściwe eksperymenty raportu. Pokazują więc, że błąd wynikający z niewłaściwej rodziny może mieć skalę porównywalną z raportowanym RMSE, a nie że na pewno wyjaśnia całe RMSE 0,148/0,153.

Lepsze sformułowanie:

> Niewłaściwie zdefiniowana rodzina referencyjna może sama generować błąd tej samej skali co raportowany RMSE. Z tego powodu obecnego RMSE nie można interpretować jako miary dokładności CEM bez ponownego obliczenia walidacji na właściwych instancjach.

Do audytu powinny zostać dołączone seedy, wagi oraz skrypt generujący podane wartości.

### 2. Równanie (20): „argmin is ill-posed”

Audyt słusznie zauważa, że oryginalny CEM używa empirycznych warunkowych wartości oczekiwanych, a raport w późniejszej części mówi o pojedynczych próbkach. Nie jest jednak prawdą, że funkcja celu z próbkami `h_j ∈ {−1,+1}` jest z konieczności źle określona albo musi wypychać optimum na granicę.

Jeżeli `m_j(β)=tanh(βΘ_j)` oraz prawdziwa wartość parametru wynosi `β₀`, to

```text
E[(h_j − m_j(β))²]
  = Var(h_j) + [m_j(β₀) − m_j(β)]²,
```

więc oczekiwana strata może mieć minimum w prawdziwym `β₀`. Taki estymator byłby po prostu bardziej zaszumiony.

Dodatkowo wcześniejsze równanie raportu, w liniach 215–217, poprawnie używa `⟨h_j⟩`. Audyt powinien zatem mówić o niespójnym lub niejednoznacznym opisie i konieczności sprawdzenia kodu, a nie o udowodnionym błędzie implementacji. Nie ma też wystarczających podstaw, aby przypisać saturację optymalizatora właśnie temu zapisowi.

### 3. Opis sektorów parzystości TFIM

Audyt trafnie wskazuje, że dla ferromagnetycznego `J>0`, `h≥0` energia sektora NS jest energią stanu podstawowego, więc `min()` w podanej formule jest zbędne. Zbyt ogólne jest jednak stwierdzenie, że drugi składnik zawsze odpowiada niedozwolonej próżni sektora R o parzystej parzystości.

Opis należy rozdzielić na reżimy `h<J` i `h>J`. Podany w audycie defekt równy `2(h−J)` dotyczy paramagnetycznego przypadku `h>J`. W obecnym brzmieniu poprawna uwaga została nadmiernie uogólniona.

### 4. Proponowana naprawa `auto_scale`

Zdanie, że po włączeniu `auto_scale` efektywna temperatura jest ustalana „purely by the device's physical temperature”, jest niepoprawnym uproszczeniem. Rozkład próbek zależy również od:

- współczynnika przeskalowania Hamiltonianu;
- funkcji `B(s)` i punktu freeze-out;
- dynamiki wyżarzania;
- osadzania i łańcuchów;
- błędów analogowych;
- odstępstw próbek od klasycznego rozkładu Boltzmanna.

Lepsza rekomendacja:

> Wyłączyć `auto_scale` w eksperymentach badających jednolite skalowanie energii albo jawnie uwzględnić wyznaczony współczynnik autoskalowania i estymować efektywną temperaturę bezpośrednio z próbek.

Zależności freeze-out opisuje dokumentacja D-Wave:

- https://docs.dwavequantum.com/en/latest/ocean/api_ref_system/generated/dwave.system.temperatures.freezeout_effective_temperature.html

### 5. Nadinterpretacja Fig. 12

Dwie uwagi są zbyt ostre:

- podpis „The dotted line marks the exact-ansatz floor” nie wskazuje złej linii; jest jedynie niejednoznaczny, ponieważ na wykresie istnieje także pionowa kropkowana linia hardware floor;
- „across the full sparsity range tested” może poprawnie odnosić się do czterech masek wyszczególnionych w tym samym akapicie, a nie do dodatkowego punktu dense przy sparsity 0.

Błędna etykieta osi `Energy error per spin |ε|/N` pozostaje natomiast prawdziwym problemem.

### 6. Niekompletny przegląd literatury

Audyt pomija bardzo bliską tematycznie pracę:

- R. J. L. F. Berns et al., *Predicting sampling advantage of stochastic Ising Machines for Quantum Simulations*, Phys. Rev. Applied 25, 024085 (2026): https://arxiv.org/abs/2504.18359

Praca dotyczy stochastic Ising machines jako samplerów dla NQS oraz jakości estymacji energii wariacyjnej. Nie odbiera automatycznie nowości dokładnemu połączeniu LSB+CEM z pętlą SR, ale znacząco zawęża pole do twierdzenia o „jedynym otwartym headline”.

Bliskim wcześniejszym wynikiem jest również:

- S. Chowdhury et al., *Probabilistic Computers for Neural Quantum States*: https://arxiv.org/abs/2512.24558

Autorzy wykorzystują probabilistyczny sprzęt FPGA jako sampler w treningu energetycznych NQS i raportują TFIM do 6400 spinów. Proponowany przez audyt tytuł „NQS-VMC trained by a simulated-bifurcation-class sampler” zbyt słabo odróżniałby nowy projekt od istniejącej literatury. Głównym wyróżnikiem musiałoby być CEM, kontrolowany bias samplera albo formalna analiza tolerancji SR.

### 7. Przeoczony problem z reprodukowalnością seedów

Audyt zbyt pozytywnie ocenia zdanie:

```text
All stochastic components (...) are seeded per run via np.random.randint
feeding jax.random.PRNGKey.
```

`np.random.randint` nie zapewnia odtwarzalności, jeżeli nie podano i nie zapisano nadrzędnego seeda NumPy oraz mapowania seedów na eksperymenty. Cache zawiera część jawnych seedów, ale raport nie opisuje kompletnego protokołu.

Do listy braków reprodukowalności należy dodać:

- nadrzędny seed generatora;
- jawne seedy każdego eksperymentu;
- sposób generowania i przechowywania kluczy JAX;
- wersje kodu powiązane z cache;
- kryteria wcześniejszego zatrzymania QPU.

### 8. Niespójna klasyfikacja ważności

Executive summary mówi o trzech defektach krytycznych w mechanizmie CEM/temperatury, tabela zawiera pięć pozycji C1–C5, a sekcja „Bottom line” podaje jeszcze inny zestaw trzech blokad.

Należy zastosować spójną klasyfikację. Przykładowo:

- **Critical:** C1, C3 i C4 — podważają interpretację głównych wyników;
- **Major:** C2, jeśli błąd dotyczy tylko zapisu, oraz problemy sektorów TFIM i zasady wariacyjnej;
- **P0 editorial:** błędne równanie (8), odwołania, etykiety i widoczne błędy językowe.

Jeżeli kod potwierdzi niewłaściwy znak CEM, C2 powinno zostać podniesione do Critical.

### 9. Drobne uwagi o małej wartości

Niektóre elementy listy minor są przestarzałe albo nie wpływają na jakość naukową:

- brak `inputenc` nie jest problemem w aktualnych dystrybucjach LaTeX, które domyślnie obsługują UTF-8;
- kolejność `\bibliography` i `\bibliographystyle` jest nietypowa, ale kompilacja działa;
- brak środowiska `table` sam w sobie nie jest brakiem reprodukowalności;
- stwierdzenie, że artykuł „potrzebuje 40–60 referencji”, nie jest uniwersalną normą i powinno zostać zastąpione listą brakujących kategorii literatury.

## Ocena stylu audytu

### Mocne strony

- bardzo dobra identyfikowalność uwag przez linie, równania i pliki;
- dobre rozdzielenie correctness, completeness, novelty, writing i reproducibility;
- konkretne rekomendacje napraw;
- priorytety P0/P1/P2;
- wskazywanie również elementów wykonanych poprawnie;
- uczciwe opisanie błędów poprzedniej wersji audytu.

### Słabe strony

- dokument jest zbyt długi jak na liczbę najważniejszych ustaleń;
- kluczowe akapity, szczególnie C1, są trudne do szybkiego przeskanowania;
- fakty, wnioskowania i rekomendacje bywają mieszane w jednym zdaniu;
- występują kategoryczne sformułowania bez wystarczającego dowodu;
- liczne bardzo precyzyjne liczby nie mają dołączonych skryptów, seedów ani danych wejściowych;
- sekcja o historii poprzedniego audytu odciąga uwagę od bieżących ustaleń;
- deklaracje typu „5–8 weeks”, „low-to-medium risk” i przewidywanie reakcji recenzentów są ocenami eksperckimi, a nie wynikiem audytu.

## Zalecana redakcja audytu

Każde istotne ustalenie powinno mieć jednolity format:

1. **Finding** — co dokładnie jest niepoprawne.
2. **Evidence** — równanie, fragment cache, wynik kompilacji albo źródło.
3. **Impact** — jaki wniosek raportu przestaje być uzasadniony.
4. **Fix** — minimalna poprawka.
5. **Confidence** — `confirmed`, `strong inference` albo `requires code inspection`.

W szczególności warto:

- skrócić C1 i przenieść liczby pomocnicze do dodatku;
- zmienić stwierdzenie o pojedynczych próbkach CEM na uwagę o niespójnym opisie;
- skorygować opis sektora R;
- poprawić rekomendację dotyczącą `auto_scale`;
- dodać Berns et al. i dokładniej pozycjonować wkład LSB+CEM;
- dodać problem z seedem nadrzędnym;
- ujednolicić poziomy Critical/Major/Minor;
- przenieść §9 do osobnego changelogu;
- dołączyć skrypty weryfikujące CEM, TFIM i statystyki cache.

## Werdykt

`audyt_cld_bg.md` jest bardzo dobrym wewnętrznym materiałem roboczym i wychwytuje kilka problemów, które rzeczywiście podważają obecne wnioski raportu. Najważniejsze z nich — zła rodzina referencyjna CEM, `auto_scale`, niematchowane budżety QPU oraz brak QPU `D_TV` i porównania kosztów — powinny zostać potraktowane poważnie.

Przed przekazaniem audytu autorowi jako formalnej recenzji należy jednak:

- osłabić nieudowodnione twierdzenia przyczynowe;
- poprawić kilka własnych błędów merytorycznych audytu;
- oddzielić fakty od spekulacji wydawniczych;
- uzupełnić przegląd literatury;
- dołączyć materiały pozwalające odtworzyć jego obliczenia.

Po tych zmianach audyt może być bardzo wartościową i wiarygodną podstawą planu napraw raportu.
