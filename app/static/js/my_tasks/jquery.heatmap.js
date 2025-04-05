// noinspection JSUnresolvedReference

/*!
 * Heatmap Plugin
 * Author: Thomas Kirsch <t.kirsch@webcito.de>
 * Version: 1.0.4
 * License: MIT
 * Description: A jQuery plugin to create and render an interactive heatmap visualization.
 *
 * Usage:
 * - Initialize the heatmap on a jQuery element. For example: $('#heatmap').heatmap(settings);
 *
 * Settings:
 * - data (Array | String): Either an array of data points or a URL from which data can be fetched.
 * - locale (String): The locale identifier for date formatting and first day of the week calculation (default: 'en-US').
 * - cellSize (Number): The size of each day cell in pixels (default: 14px).
 * - gutter (String | Number): Space between cells or weeks (default: '2px').
 * - colors (Object): A map of contribution levels to colors (e.g. `{ 0: '#ebedf0', 1: '#196127' }`).
 * - queryParams (Function): A function returning additional query parameters for data fetching.
 * - debug (Boolean): If true, logs internal events and settings to the console (default: `false`).
 * - titleFormatter (Function): A function to format tooltips for heatmap cells.
 *
 * Methods:
 * - getSettings($el): Reads and returns the heatmap settings for a given element.
 * - getData($el): Fetches or provides the data for the heatmap. Can handle local arrays or fetch from URLs.
 * - calculateWeeks(startDate, endDate, firstDayOfWeek): Computes all weeks in the given time period.
 * - drawHeatmap($el): Creates the heatmap and draws it into the provided element.
 *
 * Example:
 * $('#heatmap').heatmap({
 *    data: 'https://example.com/data',
 *    locale: 'en-US',
 *    cellSize: 14,
 *    gutter: '4px',
 *    titleFormatter: (locale, date, count) => `${date.toLocaleDateString(locale)} - ${count}`,
 *    colors: {
 *        0: '#ebedf0',
 *        0.25: '#c6e48b',
 *        0.5: '#7bc96f',
 *        0.75: '#239a3b',
 *        1: '#196127'
 *    }
 * });
 *
 * Notes:
 * - The plugin automatically calculates the first day of the week based on the provided locale.
 * - Week calculations dynamically adapt to custom start and end dates.
 * - If data is provided via URL, query parameters for startDate, endDate, and any custom params are appended.
 */
(function ($) {

    $.heatmap = {
        setDefaults: function (options) {
            this.DEFAULTS = $.extend({}, this.DEFAULTS, options || {});
        },
        getDefaults: function () {
            return this.DEFAULTS;
        },
        DEFAULTS: {
            locale: 'en-US',
            debug: false,
            classes: 'border border-5 w-100 p-5',
            data: null,
            gutter: 2,
            cellSize: 14,
            colors: {
                0: '#ebedf0',
                0.25: '#c6e48b',
                0.5: '#7bc96f',
                0.75: '#239a3b',
                1: '#196127'
            },
            titleFormatter(locale, date, count, $el) {
                const id = $el.attr('id') || '';
                return date.toLocaleDateString() + ' - ' + count + ' minutes';
            },
            queryParams(p) {
                return p;
            }
        }
    };

    function init($el, settings, draw) {
        const setup = $.extend({}, $.heatmap.DEFAULTS, settings || {});
        const localizedMoment = moment();
        const locale = setup.locale || $.heatmap.DEFAULTS.locale;
        localizedMoment.locale(locale); // Setze Locale

        $el.data('heatmapSettings', setup);

        if (setup.debug) {
            console.log('heatmap:init:', $el.data('heatmapSettings'));
        }

        if (draw) {
            drawHeatmap($el, localizedMoment); // Lokale Moment-Instanz übergeben
            $el.trigger('init.heatmap', [$el]);
        }
    }

    function getSettings($el) {
        return $el.data('heatmapSettings');
    }

    async function getData($el) {
        const settings = getSettings($el);

        if (Array.isArray(settings.data)) {
            return Promise.resolve(settings.data); // Wenn Daten ein Array sind, direkt zurückgeben
        }

        let xhr = $el.data('xhr') || null;
        if (xhr && xhr.abort) {
            xhr.abort(); // Existierende Anfrage abbrechen
            xhr = null;
        }

        const query = {};

        // Benutzerdefinierte Query-Parameter einfügen
        const customQuery = typeof settings.queryParams === 'function' ? settings.queryParams(query) : {};


        try {
            // Initialisierung der AJAX-Anfrage
            xhr = $.ajax({
                url: settings.data,  // URL der Anfrage
                method: 'GET',       // HTTP-Methode    
                data: customQuery,    // Query-Parameter
                dataType: 'json'    // Antwort automatisch als JSON parsen
            });

            $el.data('xhr', xhr); // Speichert das aktuelle xhr-Objekt beim Element

            // Warte auf die Antwort
            await xhr; // Wartet, bis die Anfrage abgeschlossen ist

            if (xhr.status === 200) { // Prüfen, ob der Statuscode erfolgreich ist
                if (settings.debug) {
                    console.log('getData: Successful Response:', xhr.responseJSON);
                }
                $el.data('xhr', null); // Reset des xhr nach Abschluss
                return xhr.responseJSON; // JSON-Daten zurückgeben (die Antwort vom Server)
            } else {
                throw new Error(`getData: Fehlerhafter Statuscode ${xhr.status}: ${xhr.statusText}`);
            }
        } catch (error) {
            $el.data('xhr', null); // Reset auch im Fehlerfall
            if (settings.debug) {
                console.error('getData:error', error);
            }
            throw error; // Fehler weitergeben
        }
    }

    // Berechnung aller Wochen eines Jahres (ink. angrenzender Wochen aus Vor- und Folgejahr)
    function calculateWeeks($el, startDate, endDate, firstDayOfWeek) {
        const settings = getSettings($el);

        // Start- und Ende-Datum verarbeiten
        const start = getStartOfWeek(new Date(startDate), firstDayOfWeek);
        const end = getEndOfWeek(new Date(endDate), firstDayOfWeek);

        if (settings.debug) {
            console.log('DEBUG: calculateWeeks:', {
                startDate,
                endDate,
                firstDayOfWeek,
                start: start.toISOString(),
                end: end.toISOString(),
            });
        }

        const weeks = [];
        let currentDate = new Date(start);

        // Wochenberechnung
        while (currentDate <= end) {
            const currentWeek = [];

            for (let i = 0; i < 7; i++) { // Erstelle eine Woche (7 Tage)
                currentWeek.push(new Date(currentDate));
                currentDate.setUTCDate(currentDate.getUTCDate() + 1); // Use UTC date
             //   currentDate.setDate(currentDate.getDate() + 1); // Einen Tag vorwärts
            }

            weeks.push(currentWeek);
        }

        if (settings.debug) {
            console.log('DEBUG: Berechnete Wochen:', weeks);
        }

        return weeks;
    }

    // O problema está aqui!!!!!!!!! 
    // {startDate: '2024-02-02', endDate: '2025-02-02', firstDayOfWeek: 0, start: '2024-01-28T03:00:00.000Z', end: '2025-02-02T02:59:59.999Z'}
    // end deveria ser dia 08/02/2025.
    // o startOfWeek está pegando o dia 26/01 inves do dia 02/02, será que é erro de fuso horário?

    function getEndOfWeek(date, firstDayOfWeek) {
        const startOfWeek = getStartOfWeek(date, firstDayOfWeek);
        const end = new Date(startOfWeek);
        end.setDate(startOfWeek.getDate() + 6); // 6 Tage nach dem Startdatum
        end.setHours(23, 59, 59, 999); // Uhrzeit auf Ende des Tages setzen
        console.log('startOfWeek.getDate() ', startOfWeek.getDate())
        console.log('end ', end)
        return end;
    }

    function getStartOfWeek(date, firstDayOfWeek) {
        const currentDay = date.getDay(); // Aktueller Tag (0=Sonntag, 6=Samstag)
        const diff = (currentDay - firstDayOfWeek + 7) % 7; // Unterschied zum ersten Tag berechnen

        const start = new Date(date);
        start.setDate(date.getDate() - diff); // Zurücksetzen zum Start der Woche
        start.setHours(0, 0, 0, 0); // Uhrzeit auf Mitternacht
        return start;
    }

    // function getStartOfWeek(date, firstDayOfWeek) {
    //     const currentDay = date.getUTCDay();
    //     const diff = (currentDay - firstDayOfWeek + 7) % 7;
    
    //     const start = new Date(date);
    //     start.setUTCDate(date.getUTCDate() - diff);
    //     start.setUTCHours(0, 0, 0, 0);
    
    //     console.log('Start of Week (UTC):', start.toISOString());
    //     return start;
    // }
    
    // function getEndOfWeek(date, firstDayOfWeek) {
    //     const startOfWeek = getStartOfWeek(date, firstDayOfWeek);
    //     const end = new Date(startOfWeek);
    //     end.setUTCDate(startOfWeek.getUTCDate() + 6);
    //     end.setUTCHours(23, 59, 59, 999);
    
    //     console.log('End of Week (UTC):', end.toISOString());
    //     return end;
    // }

    function drawHeatmap($el, myMoment) {
        const settings = getSettings($el);
        // Validierung der Einstellungen
        if (!settings) {
            console.error('Keine Heatmap-Einstellungen gefunden, Abbruch');
            return;
        }

        if (settings.debug) {
            console.log('heatmap:drawHeatmap');
        }


        // Zell- und Abstandseinstellungen
        let gutter = (settings.gutter !== undefined ? settings.gutter : '2px');
        if (typeof gutter === 'number') {
            gutter = `${gutter}px`;
        }
        const cellSize = settings.cellSize || 14;
        const cellSizePx = `${cellSize}px`;

        $el.empty();

        // Daten abrufen
        getData($el).then(rawData => {
            const data = Array.isArray(rawData) ? rawData : JSON.parse(rawData);
            if (!Array.isArray(data)) {
                throw new Error('Die erhaltenen Daten sind kein Array.');
            }

            if (settings.debug) {
                console.log('heatmap:drawHeatmap:data', data);
            }
            const monthFormatter = new Intl.DateTimeFormat(myMoment.locale(), {month: 'short'});
            const firstDayOfWeek = getFirstDayOfWeek(myMoment);

            let startDate;
            let endDate;
            
            
            // 1o caso -> Gera o gráfico a partir de todas as datas enviadas, calculando o inicio e o fim

            // if (data.length === 0) {
            //     const currentYear = new Date().getFullYear();
            //     startDate = new Date(`${currentYear}-01-01`);
            //     endDate = new Date(`${currentYear}-12-31`);
            // } else {
            //     startDate = new Date(data[0].date);
            //     endDate = new Date(data[0].date);

            //     for (const entry of data) {
            //         const entryDate = new Date(entry.date);
            //         if (entryDate < startDate) {
            //             startDate = entryDate;
            //         }
            //         if (entryDate > endDate) {
            //             endDate = entryDate;
            //         }
            //     }
            // }
            // endDate.setDate(endDate.getDate() + 1);
            

            // 2o caso -> Pega a ultima data enviada e calcula 1 ano antes dela como o inicio

            // endDate = data.length > 0 ? data[0].date : new Date().toISOString().split('T')[0];
            // for (const entry of data) {
            //     if (entry.date > endDate) {
            //         endDate = entry.date;
            //     }
            // }
            // const endDateParts = endDate.split('-');
            // startDate = `${endDateParts[0] - 1}-${endDateParts[1]}-${endDateParts[2]}`;



           
            // 3o caso -> pega a data de hoje como data final e 1 ano antes como data inicial independente dos dados recebidos

            // Nesse caso a data final sempre será o dia de hoje e o dia inicial será 1 ano antes do dia de hj (qu é exatamente oque precisamos para nosso gráfico, caso precisemos de outra solução, podemos ultilizar os exemplos acima)
            // Pensar no caso de ver por ano ou por mês.
            // Nesse caso o endDate e o startData precisaria ser um parâmetro.
            const today = new Date();
            endDate = today.toISOString().split('T')[0];

            startDate = new Date();
            startDate.setFullYear(startDate.getFullYear() - 1); // Subtract 1 year
            startDate = startDate.toISOString().split('T')[0];

            // endDate = new Date().toISOString().split('T')[0];
            // const endDateParts = endDate.split('-');
            // startDate = `${endDateParts[0] - 1}-${endDateParts[1]}-${endDateParts[2]}`;

          

            // Wochen und Daten vorbereiten
            const weeks = calculateWeeks($el, startDate, endDate, firstDayOfWeek);

            // Create a new dataMap using date strings as keys
            // Alterei esse caso para não haver nenhuma alteração ao enviar os dados, independente do fuso horário do usuário, a data será a mesma que a enviada
            const dataMap = new Map();
            for (let entry of data) {
                // const entryDate = new Date(entry.date);
                // const dayKey = new Date(Date.UTC(entryDate.getFullYear(), entryDate.getMonth(), entryDate.getDate())).toISOString().split('T')[0];
                // console.log('Testando os entry: ' + entry.date, entryDate, dayKey)
                // console.log('Testando os entry: ' + entry.date)
                dataMap.set(entry.date, entry.count);
            }
            if (settings.debug) {
                console.log('Berechnete Wochen:', weeks);
            }

            const counts = data
                .map(entry => entry.count)
                .filter(count => typeof count === 'number' && count >= 0); // Nur gültige Zahlenwerte

            const fallbackMin = 0;  // Fallback für minCount
            const fallbackMax = 1;  // Fallback für maxCount (z. B. 1 für eine minimale Skalierung)

            const hasValidCounts = counts.length > 0;

            const minCount = hasValidCounts ? Math.min(...counts) : fallbackMin;
            const maxCount = hasValidCounts ? Math.max(...counts) : fallbackMax;
            // console.log("MinCount: ", minCount)
            // console.log("MaxCount: ", maxCount)

            if (settings.debug) {
                console.log('DEBUG: Min-/Max-Werte:', {minCount, maxCount, hasValidCounts});
            }

            // Farben cachen
            const colorCache = {};

            function getCachedColor(count) {
                const cacheKey = `${count}-${minCount}-${maxCount}`;

                if (colorCache[cacheKey]) {
                    return colorCache[cacheKey];
                }

                const color = getContributionColor($el, count, minCount, maxCount);
                colorCache[cacheKey] = color;
                return color;
            }

            // Wochen vorbereiten (Tage mit Zählwerten verbinden)
            weeks.forEach(week => {
                week.forEach((day, index) => {
                    const dayKey = new Date(Date.UTC(day.getFullYear(), day.getMonth(), day.getDate())).toISOString().split('T')[0]; // toISOString verwendet lokale Zeitzone
                    week[index] = {
                        date: day,
                        count: dataMap.get(dayKey) || 0,
                    };
                });
            });

            // Heatmap-Container erstellen
            const heatmapContainer = $('<div class="heatmap-wrapper"></div>');
            heatmapContainer.css({
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'flex-start',
                gap: gutter,
            });

            const placeholder = $('<div class="month-placeholder"></div>'); // Platzhalter für Monatsnamen
            placeholder.css({
                height: cellSizePx, // Höhe der Monatsnamen-Zeile
                width: '100%',
            });

            // Tagesnamen-Spalte (Montag, Dienstag, ...)
            const dayLabelColumn = $('<div class="day-labels"></div>');
            dayLabelColumn.append(placeholder); // Platzhalter hinzufügen
            dayLabelColumn.css({
                display: 'grid',
                gridTemplateRows: `${cellSizePx} repeat(7, ${cellSizePx})`,
                marginRight: gutter,
                textAlign: 'right',
                rowGap: gutter,
            });

            Array.from({length: 7}, (_, i) => (firstDayOfWeek + i) % 7)
                .forEach(dayOffset => {
                    const tempDate = myMoment.clone().isoWeekday(dayOffset === 0 ? 7 : dayOffset); // 1=Mo, 7=So
                    const label = $('<div class="day-label"></div>');
                    label.text(tempDate.format('ddd')); // Lokalisierter Tagesname
                    label.css({
                        fontSize: `${cellSize * 0.7}px`,
                        color: '#ffffff',
                        textAlign: 'center',
                        lineHeight: cellSizePx,
                    });
                    dayLabelColumn.append(label);
                });

            heatmapContainer.append(dayLabelColumn);

            // Wochen und Zellen rendern
            const heatmapGrid = $('<div class="heatmap"></div>');
            heatmapGrid.css({
                display: 'flex',
                gap: gutter,
            });

            let lastRenderedMonth = -1;

            weeks.forEach(week => {
                const weekColumn = $('<div class="heatmap-week"></div>');
                weekColumn.css({
                    display: 'grid',
                    gridTemplateRows: `${cellSizePx} repeat(7, ${cellSizePx})`,
                    rowGap: gutter,
                });

                // Monatsnamen hinzufügen
                const currentMonth = week.find(d => d.date && d.date.getDate() === 1)?.date.getMonth();
                if (currentMonth !== undefined && currentMonth !== lastRenderedMonth) {
                    lastRenderedMonth = currentMonth;
                    const monthLabel = $('<div class="month-label"></div>');
                    monthLabel.text(monthFormatter.format(week.find(d => d.date && d.date.getDate() === 1).date));
                    monthLabel.css({
                        textAlign: 'left',
                        fontSize: `${cellSize * 0.7}px`,
                        lineHeight: cellSizePx,
                        height: cellSizePx,
                        width: cellSizePx,
                    });
                    weekColumn.append(monthLabel);
                } else {
                    weekColumn.append('<div style="height: ' + cellSizePx + ';"></div>');
                }

                // Tageszellen rendern
                week.forEach(dayEntry => {
                    const cell = $('<div class="heatmap-cell"></div>');
                    const today = new Date();
                    const todayUTC = new Date(Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()));
                    const cellDate = new Date(Date.UTC(dayEntry.date.getFullYear(), dayEntry.date.getMonth(), dayEntry.date.getDate())); 

                    cell.css({
                        width: cellSizePx,
                        height: cellSizePx,
                        backgroundColor: getCachedColor(dayEntry.count),
                        borderRadius: parseInt(gutter) > 2 ? '6px' : gutter,
                        cursor: 'pointer',
                        border: '1px solid rgba(255, 255, 255, 0.1)'
                    });

                    if (cellDate.toISOString().split('T')[0] === todayUTC.toISOString().split('T')[0]) {
                        // Optional:  HINTERGRUNDFARBE anpassen. Zuerst die aktuelle Farbe ermitteln
                        //const currentColor = cell.css('background-color');
                        //cell.css('background-color', shadeColor(currentColor, 0.2)); // 20% heller
                        console.log(`Today's cell: ${cellDate.toISOString()}`);
                        cell.css("border", "1px solid rgb(207, 254, 216)");
                    }


                    if (dayEntry.date) {
                        cell
                            .attr('data-bs-toggle', 'tooltip') // Bootstrap 5
                            .attr('data-bs-custom-class', 'info-tooltip')
                            .attr('data-bs-html', true) // Tooltip mit HTML
                            .attr(
                                'title',
                                settings.titleFormatter(settings.locale, dayEntry.date, dayEntry.count, $el) || ''
                            );
                    }

                    weekColumn.append(cell);
                });

                heatmapGrid.append(weekColumn);
            });

            heatmapContainer.append(heatmapGrid);
            $el.append(heatmapContainer);
            $el.trigger('post.heatmap', [$el, data]);
        }).catch(err => {
            console.error('Fehler beim Laden der Daten:', err);
            $el.append(`<div class="heatmap-error">${err.message || err}</div>`);
        }).finally(() => {

        });
    }
    function shadeColor(color, percent) {
        let R = parseInt(color.substring(1,3),16);
        let G = parseInt(color.substring(3,5),16);
        let B = parseInt(color.substring(5,7),16);

        R = parseInt(R * (100 + percent) / 100);
        G = parseInt(G * (100 + percent) / 100);
        B = parseInt(B * (100 + percent) / 100);

        R = (R<255)?R:255;
        G = (G<255)?G:255;
        B = (B<255)?B:255;

        const RR = ((R.toString(16).length==1)?"0"+R.toString(16):R.toString(16));
        const GG = ((G.toString(16).length==1)?"0"+G.toString(16):G.toString(16));
        const BB = ((B.toString(16).length==1)?"0"+B.toString(16):B.toString(16));

        return "#"+RR+GG+BB;
    }


    function findStartOfWeek(date, firstDayOfWeek) {
        const currentDay = date.getDay(); // Wochentag des aktuellen Datums (0=Sonntag, 6=Samstag)
        const diff = (currentDay - firstDayOfWeek + 7) % 7; // Differenz berechnen: Rücksprung zum Wochentag
        const startOfWeek = new Date(date);
        startOfWeek.setDate(date.getDate() - diff); // Berechne den Start der Woche
        startOfWeek.setHours(0, 0, 0, 0); // Uhrzeit auf 00:00 setzen
        return startOfWeek;
    }

// Unterstützungsfunktion: Ermitteln, ob die Woche mit Montag oder Sonntag startet
    function getFirstDayOfWeek(myMoment) {
        // Hole die erste-Wochentag-Informationen von momentForHeatmap
        console.log(myMoment.localeData().firstDayOfWeek())
        return myMoment.localeData().firstDayOfWeek();
    }


// Unterstützungsfunktion: Farbskala für Contributions
    function getContributionColor($el, count, minCount, maxCount) {
        const settings = getSettings($el);

        if (!settings.colors || Object.keys(settings.colors).length === 0) {
            settings.colors = $.heatmap.DEFAULTS.colors;
        }

        // Sonderfall für count = 0
        if (count === 0) {
            return settings.colors['0'];
        }

        // Evita divisão por zero e corrige range quando minCount = 0
        const safeMin = Math.max(1, minCount);
        const safeCount = Math.max(1, count);
        const safeMax = Math.max(safeMin + 1, maxCount);

        // Normalização logarítmica ajustada
        const rangeLog = Math.log(safeMax) - Math.log(safeMin);
        let scaledPercentage = (Math.log(safeCount) - Math.log(safeMin)) / rangeLog;

        // Ajuste linear para evitar que valores médios fiquem muito altos
        scaledPercentage = Math.pow(scaledPercentage, 2.3); // Ajuste exponencial

        scaledPercentage = Math.max(0, Math.min(scaledPercentage, 1));


        // Farbschlüssel erhalten und sortieren
        const colorKeys = Object.keys(settings.colors)
            .map(Number) // Keys zu Zahlen umwandeln
            .sort((a, b) => a - b); // Keys aufsteigend sortiert

        // Standard-Logik: Zu einem passenden Farbschlüssel mappen
        let matchedKey = colorKeys.find(key => scaledPercentage <= key) || Math.max(...colorKeys);

        // Für den minimalen Wert auf die erste sichtbare Stufe fallen
        if (count !== 0 && count === minCount) {
            matchedKey = colorKeys.find(key => key > 0) || Math.max(...colorKeys);
        }

        // Farbe auswählen (mit Fallback auf `1`)
        let color = settings.colors[matchedKey] || settings.colors['1'];

        if (settings.debug) {
            console.log('DEBUG: Farbzuordnung:', {
                count,
                minCount,
                maxCount,
                rangeLog,
                scaledPercentage,
                matchedKey,
                color
            });
        }

        return color;
    }

    function adjustStartDate(startDate, locale, firstDayOfWeek, debug) {
        if (!startDate) {
            return null; // Kein Datum vorhanden, nichts anpassen
        }

        const originalStartDate = new Date(startDate);
        const adjustedStartDate = findStartOfWeek(originalStartDate, firstDayOfWeek); // Datum berechnen
        const formattedStartDate = adjustedStartDate.toISOString().split('T')[0]; // Als 'YYYY-MM-DD'

        if (debug) {
            console.log('DEBUG: Startdatum angepasst:', {
                original: originalStartDate.toISOString(),
                adjusted: adjustedStartDate.toISOString(),
                formatted: formattedStartDate,
                firstDayOfWeek: firstDayOfWeek,
                locale: locale
            });
        }

        return formattedStartDate; // Formatiertes Datum zurückgeben
    }

    $.fn.heatmap = function (options, params) {
        if ($(this).length > 1) {
            return $(this).each(function (i, element) {
                return $(element).heatmap(options, params);
            });
        }

        const $element = $(this);
        const momentForHeatmap = moment();

        const methodCalled = typeof options === 'string';
        const isInitialized = $element.data('heatmapSettings');

        if (!isInitialized) {
            console.log('>>>>>>>>>>>>>><<', options);
            init($element, options, !methodCalled);
        }

        // Rückgabewert für Methodenaufruf oder Initialisierung
        if (!methodCalled) {
            return $element; // Kein Methodenaufruf, Initialisierung abgeschlossen
        }

        switch (options) {
            case 'updateOptions': {
                const setup = $element.data('heatmapSettings');
                if (setup.debug) {
                    console.log('heatmap:updateOptions', params);
                }

                const updatedSetup = $.extend({}, $.heatmap.DEFAULTS, setup, params || {});
                const myMoment = moment().locale(updatedSetup.locale || $.heatmap.DEFAULTS.locale);

                // const firstDayOfWeek = getFirstDayOfWeek(myMoment);
                // updatedSetup.startDate = adjustStartDate(
                //     updatedSetup.startDate,
                //     updatedSetup.locale,
                //     firstDayOfWeek,
                //     updatedSetup.debug
                // );

                $element.data('heatmapSettings', updatedSetup);
                drawHeatmap($element, myMoment);
            }
                break;
        }

        return $element;
    }
}(jQuery));
