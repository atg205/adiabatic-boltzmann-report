# Ocena `audyt_cld_bg.md`

**Ocena ogólna: 7/10.** To wartościowy i miejscami bardzo dobry audyt techniczny, ale w obecnej wersji nie powinien być traktowany jako ostateczna, w pełni zweryfikowana recenzja. Największy problem polega na tym, że dokument deklaruje pełne ponowne zakotwiczenie ustaleń w bieżącym `report.tex`, chociaż część wniosków pochodzi ze starszego commita.

## Najważniejsze błędy audytu

### 1. B1 jest już fałszywy

Audyt nadal zgłasza sprzeczność dotyczącą `auto_scale`, lecz aktualny raport mówi `auto_scale=False` zarówno w sekcji eksperymentalnej (`report.tex`, linia 349), jak i w konfiguracji sprzętu (`report.tex`, linia 676). Sprzeczność występowała w starszym commicie, ale została usunięta przed powstaniem bieżącej wersji audytu. B1 oraz odpowiadający mu punkt P0 należy wykreślić.

### 2. Ocena reprodukowalności została oparta na zbyt wąskim zakresie repozytorium

Audyt twierdzi, że nie ma aktualnego skryptu TTE, danych ani pliku `requirements.txt`. Tymczasem repozytorium implementacji wskazane bezpośrednio w raporcie zawiera:

- funkcje generujące aktualne figury TTE i energii wraz z walidowanym kryterium zbieżności;
- archiwum wyników TTE;
- dane eksperymentu `auto_scale`;
- plik `requirements.txt`, choć bez przypiętych wersji bibliotek.

Stan ten zweryfikowano 18 sierpnia 2026 r. na publicznym commicie [`a4b0f200`](https://github.com/iitis/adiabatic-boltzmann/commit/a4b0f2006cf0b5bf3a7ae40cea70093a5fab9d41), między innymi w [`scripts/viz/paper_figures.py`](https://github.com/iitis/adiabatic-boltzmann/blob/a4b0f2006cf0b5bf3a7ae40cea70093a5fab9d41/scripts/viz/paper_figures.py) i [`requirements.txt`](https://github.com/iitis/adiabatic-boltzmann/blob/a4b0f2006cf0b5bf3a7ae40cea70093a5fab9d41/requirements.txt).

Ocena D+ może nadal okazać się uzasadniona po próbie pełnego odtworzenia wyników w czystym środowisku, ale jej obecne uzasadnienie jest częściowo nieaktualne. Audyt powinien przypiąć konkretny commit repozytorium implementacji i oceniać oba repozytoria łącznie.

### 3. Pominięto część materiału dodanego w `final changes`

Wbrew sekcji 5 audytu:

- afiliacja jest podana w `report.tex`, linie 41–44;
- benchmark jest określony jako TFIM przy `h=0.5`, a seedy jako 0–19 w linii 678;
- parametry LSB znajdują się w tabeli w okolicy linii 689;
- konfiguracja FPGA/VeloxQ została przynajmniej technicznie opisana w linii 676.

Nie wszystkie braki zostały usunięte — przykładowo liczba jednostek ukrytych powinna być podana bezpośrednio przy głównym benchmarku — ale obecne sformułowania audytu są zbyt kategoryczne.

### 4. Sekcja dotycząca energii błędnie zakłada porównanie z QPU

Audyt sugeruje, że twierdzenie o efektywności energetycznej dziedziczy asymetrię zegara QPU. Raport jawnie wyklucza jednak D-Wave z wykresu energii (`report.tex`, linia 544), ponieważ nie ma telemetrii energii pojedynczego zadania.

Prawdziwy problem jest inny i nawet poważniejszy redakcyjnie: abstrakt mówi o przewadze FPGA nad samplerami „classical and quantum alike” w obu metrykach, chociaż energia QPU nie została zmierzona. Zarzut powinien dotyczyć braku podstaw do tego zdania, a nie asymetrycznego pomiaru energii QPU.

### 5. Część ustaleń oznaczonych jako `confirmed` jest tylko hipotezą albo interpretacją

Dotyczy to zwłaszcza:

- określenia seeding przez `np.random.randint` jako niereprodukowalnego „z definicji” — wywołanie może być deterministyczne po wcześniejszym ustawieniu globalnego seeda;
- dokładnego efektu „około 14×” przypisanego kryterium CV — z samego skalowania `N^{-1/2}` nie wynika uniwersalna relacja z błędem energii;
- „arytmetycznej niezgodności” czasów QPU wyprowadzonej pośrednio z położenia markerów;
- interpretacji zwrotu „every other size” jako zaprzeczenia luce, mimo że raport od razu podaje jednoznaczny zbiór `{8,16,32,64}`;
- stwierdzenia, że rekord bibliograficzny został „invented” wyłącznie na podstawie pustych metadanych PDF. Źródło nie wspiera twierdzenia o modelu Heisenberga i powinno zostać wymienione, ale brak metadanych nie dowodzi sfabrykowania rekordu.

Te punkty powinny zostać oznaczone jako `inference`, `requires code inspection` albo zapisane ostrożniej.

### 6. Hierarchia priorytetów wymaga korekty

B5 i B6 dotyczą podstaw głównego porównania solverów: nieporównywalnych zegarów oraz estymatora obciążonego przeżywalnością. Są ważniejsze dla wiarygodności wyniku niż część pozycji umieszczonych obecnie w P0, zwłaszcza nieaktualne B1 i kilka braków bibliograficznych. Powinny zostać przeniesione do grupy „przed udostępnieniem manuskryptu”.

## Co audyt robi bardzo dobrze

Najsilniejsze ustalenia pozostają trafne i ważne:

- prywatny dokument bankowy nadal znajduje się w historii publicznego `origin/main`; jest to rzeczywiste i pilne P0;
- B2 poprawnie wykazuje, że opis kolejności solverów przeczy własnemu wykresowi;
- B3 trafnie wskazuje nadinterpretację przewagi FPGA i skalowania w abstrakcie oraz Conclusion;
- B4 poprawnie wykazuje sprzeczność między zdaniem o testach wyłącznie klasycznych a committowanym cache QPU;
- B5 słusznie kwestionuje porównanie `qpu_access_time` z pełniejszym zegarem metod klasycznych;
- B6 trafnie zauważa, że mediana liczona wyłącznie po udanych seedach jest obciążona selekcją, a przy mniej niż połowie zdarzeń właściwa mediana TTE nie jest zidentyfikowana;
- braki cytowań i pozycjonowania literaturowego zostały dobrze rozpoznane;
- analiza average sign w niezrotowanej bazie jest interesująca i merytorycznie cenna;
- audyt jest konkretny, oparty na liczbach i zazwyczaj proponuje wykonalne poprawki.

## Oceny cząstkowe

| Kryterium | Ocena |
|---|---:|
| Trafność głównych problemów manuskryptu | 8/10 |
| Aktualność względem bieżącego `report.tex` | 5/10 |
| Rzetelność oznaczeń pewności | 6,5/10 |
| Ocena reprodukowalności | 5,5/10 |
| Struktura i użyteczność praktyczna | 8,5/10 |
| Styl i czytelność | 8/10 |
| Gotowość jako formalna recenzja | 6,5/10 |

## Zalecana Revision 9

Przed użyciem audytu jako formalnej recenzji należy:

1. przypiąć dokładne SHA zarówno raportu, jak i repozytorium implementacji;
2. usunąć B1 i ponownie sprawdzić wszystkie ustalenia dotyczące materiału z `final changes`;
3. przepisać sekcję reprodukowalności po inspekcji publicznego repozytorium implementacji i, najlepiej, próbie odtworzenia figur w czystym środowisku;
4. poprawić analizę metryki energii, wskazując brak danych QPU zamiast asymetrii nieistniejącego pomiaru;
5. obniżyć pewność B8 oraz wniosków o skalowaniu CV i czasach minimalnej liczby iteracji;
6. awansować problemy z zegarem i cenzorowaniem do właściwego P0 metodologicznego;
7. oddzielić fakty bieżące od usterek historycznych już naprawionych;
8. skrócić powtórzenia między podsumowaniem, opisem szczegółowym i listą priorytetów.

## Werdykt końcowy

`audyt_cld_bg.md` jest bardzo dobrym materiałem roboczym i wykrywa kilka rzeczywistych problemów blokujących wiarygodność manuskryptu. Nie jest jednak jeszcze wiarygodnym „stanem końcowym”, ponieważ zawiera co najmniej jeden fałszywy blocker, kilka nieaktualnych braków oraz istotnie zaniża stan artefaktów reprodukcyjnych dostępnych w repozytorium implementacji.

Po usunięciu tych problemów audyt mógłby osiągnąć około **9/10**. Obecny plik `uwagi_do_audytu_cld_bg.md` nie stanowi aktualnego potwierdzenia Revision 8, ponieważ jego własny nagłówek mówi, że oceniał Revision 6.
