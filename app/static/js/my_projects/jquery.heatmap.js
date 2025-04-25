// noinspection JSUnresolvedReference

/*!
 * Heatmap Plugin (UTC & Sunday Start Version)
 * Author: Thomas Kirsch <t.kirsch@webcito.de>
 * Version: 1.0.5 (Modified for UTC/Sunday Start)
 * License: MIT
 * Description: A jQuery plugin to create and render an interactive heatmap visualization using UTC dates and a fixed Sunday week start.
 *
 * Usage:
 * - Initialize the heatmap on a jQuery element. For example: $('#heatmap').heatmap(settings);
 *
 * Settings:
 * - data (Array | String): Either an array of data points (expected format: [{ date: 'YYYY-MM-DD', count: N }, ...]) or a URL from which data can be fetched.
 * - locale (String): The locale identifier for date *display* formatting (month names, day names) (default: 'en-US'). Week calculation is fixed to Sunday start.
 * - cellSize (Number): The size of each day cell in pixels (default: 14px).
 * - gutter (String | Number): Space between cells or weeks (default: '2px').
 * - colors (Object): A map of contribution levels to colors (e.g. `{ 0: '#ebedf0', 1: '#196127' }`).
 * - queryParams (Function): A function returning additional query parameters for data fetching.
 * - debug (Boolean): If true, logs internal events and settings to the console (default: `false`).
 * - titleFormatter (Function): A function to format tooltips for heatmap cells. Receives UTC date object.
 *
 * Methods:
 * - getSettings($el): Reads and returns the heatmap settings for a given element.
 * - getData($el): Fetches or provides the data for the heatmap. Can handle local arrays or fetch from URLs.
 * - calculateWeeks(startDateStr, endDateStr): Computes all weeks (Sun-Sat) in the given UTC time period.
 * - drawHeatmap($el): Creates the heatmap and draws it into the provided element using UTC.
 *
 * Example:
 * $('#heatmap').heatmap({
 *    data: 'https://example.com/data', // Expects JSON like [{ "date": "2024-01-15", "count": 5 }, ...]
 *    locale: 'pt-BR', // For month/day names like 'Jan', 'Dom', 'Seg'
 *    cellSize: 14,
 *    gutter: '4px',
 *    titleFormatter: (locale, utcDate, count) => {
 *        // Format UTC date for display (example using Intl.DateTimeFormat)
 *        const dateString = new Intl.DateTimeFormat(locale, {
 *            year: 'numeric', month: 'numeric', day: 'numeric', timeZone: 'UTC'
 *        }).format(utcDate);
 *        return `${dateString} - ${count}`;
 *     },
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
 * - All date calculations are performed in UTC.
 * - The week always starts on Sunday (day 0) and ends on Saturday (day 6).
 * - Input data dates should be in 'YYYY-MM-DD' format, representing UTC dates.
 * - Tooltips receive a UTC Date object. Formatting should handle this appropriately.
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
            locale: 'en-US', // Used for display formatting (month/day names)
            debug: false,
            classes: 'border border-5 w-100 p-5',
            data: null, // Expects [{ date: 'YYYY-MM-DD', count: N }, ...] or URL
            gutter: 2,
            cellSize: 14,
            colors: {
                0: '#ebedf0',
                0.25: '#c6e48b',
                0.5: '#7bc96f',
                0.75: '#239a3b',
                1: '#196127'
            },
            // Receives a UTC Date object
            titleFormatter(locale, utcDate, count, $el) {
                const id = $el.attr('id') || '';
                 // Example: Format UTC date using Intl.DateTimeFormat for locale-specific display
                 const dateString = new Intl.DateTimeFormat(locale, {
                     year: 'numeric', month: 'numeric', day: 'numeric', timeZone: 'UTC'
                 }).format(utcDate);
                return dateString + ' - ' + count + ' minutes';
            },
            queryParams(p) {
                return p;
            }
        }
    };

    function init($el, settings, draw) {
        const setup = $.extend({}, $.heatmap.DEFAULTS, settings || {});
        // Moment is only used for locale-specific formatting (month/day names)
        const localizedMoment = moment();
        const locale = setup.locale || $.heatmap.DEFAULTS.locale;
        localizedMoment.locale(locale); // Set locale for formatting

        $el.data('heatmapSettings', setup);

        if (setup.debug) {
            console.log('heatmap:init (UTC Mode):', $el.data('heatmapSettings'));
        }

        if (draw) {
            // Pass the moment instance for formatting, but calculations are UTC
            drawHeatmap($el, localizedMoment);
            $el.trigger('init.heatmap', [$el]);
        }
    }

    function getSettings($el) {
        return $el.data('heatmapSettings');
    }

    async function getData($el) {
        const settings = getSettings($el);

        if (Array.isArray(settings.data)) {
            // Ensure data dates are treated as UTC 'YYYY-MM-DD' strings
            return Promise.resolve(settings.data);
        }

        let xhr = $el.data('xhr') || null;
        if (xhr && xhr.abort) {
            xhr.abort();
            xhr = null;
        }

        const query = {};
        const customQuery = typeof settings.queryParams === 'function' ? settings.queryParams(query) : {};

        try {
            xhr = $.ajax({
                url: settings.data,
                method: 'GET',
                data: customQuery,
                dataType: 'json'
            });

            $el.data('xhr', xhr);
            await xhr;

            if (xhr.status === 200) {
                if (settings.debug) {
                    console.log('getData: Successful Response:', xhr.responseJSON);
                }
                $el.data('xhr', null);
                 // Assume responseJSON is [{ date: 'YYYY-MM-DD', count: N }, ...]
                return xhr.responseJSON;
            } else {
                throw new Error(`getData: Error status ${xhr.status}: ${xhr.statusText}`);
            }
        } catch (error) {
            $el.data('xhr', null);
            if (settings.debug) {
                console.error('getData:error', error);
            }
            throw error;
        }
    }

    // Calculates the UTC start of the week (Sunday) for a given UTC date.
    function getStartOfWeekUTC(date) {
        // Create a date object explicitly in UTC
        const utcDate = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
        const dayOfWeek = utcDate.getUTCDay(); // 0=Sunday, 1=Monday, ..., 6=Saturday
        const diff = dayOfWeek; // Difference to Sunday (day 0)
        utcDate.setUTCDate(utcDate.getUTCDate() - diff); // Go back to Sunday
        utcDate.setUTCHours(0, 0, 0, 0); // Set to start of the UTC day
        return utcDate;
    }

    // Calculates the UTC end of the week (Saturday) for a given UTC date.
    function getEndOfWeekUTC(date) {
        // Create a date object explicitly in UTC
        const utcDate = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
        const startOfWeek = getStartOfWeekUTC(utcDate); // Get Sunday 00:00:00 UTC
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setUTCDate(startOfWeek.getUTCDate() + 6); // Add 6 days to get Saturday
        endOfWeek.setUTCHours(23, 59, 59, 999); // Set to end of the UTC day
        return endOfWeek;
    }

    // Calculate all weeks (Sunday-Saturday) within the given UTC date range.
    // Expects startDateStr and endDateStr in 'YYYY-MM-DD' format (representing UTC dates).
    function calculateWeeks($el, startDateStr, endDateStr) {
        const settings = getSettings($el);
        const firstDayOfWeek = 0; // Hardcoded to Sunday

        // Parse the date strings as UTC dates. Appending 'T00:00:00Z' ensures UTC interpretation.
        const startDate = new Date(startDateStr + 'T00:00:00Z');
        const endDate = new Date(endDateStr + 'T00:00:00Z');

        // Get the start of the week containing the startDate (Sunday)
        const start = getStartOfWeekUTC(startDate);
        // Get the end of the week containing the endDate (Saturday)
        const end = getEndOfWeekUTC(endDate);

        if (settings.debug) {
            console.log('DEBUG: calculateWeeks (UTC):', {
                startDateInput: startDateStr,
                endDateInput: endDateStr,
                firstDayOfWeekForced: firstDayOfWeek,
                calculatedStartUTC: start.toISOString(),
                calculatedEndUTC: end.toISOString(),
            });
        }

        const weeks = [];
        let currentDate = new Date(start); // Start from the calculated Sunday UTC

        // Loop through weeks until we pass the calculated end date
        while (currentDate <= end) {
            const currentWeek = [];
            for (let i = 0; i < 7; i++) { // Create a week (7 days)
                currentWeek.push(new Date(currentDate)); // Add the current UTC date
                currentDate.setUTCDate(currentDate.getUTCDate() + 1); // Move to the next UTC day
            }
            weeks.push(currentWeek);
        }

        if (settings.debug) {
            console.log('DEBUG: Calculated Weeks (UTC):', weeks.map(w => w.map(d => d.toISOString())));
        }

        return weeks;
    }


    function drawHeatmap($el, myMoment) { // myMoment is for locale formatting only
        const settings = getSettings($el);
        if (!settings) {
            console.error('Heatmap settings not found, aborting draw.');
            return;
        }

        if (settings.debug) {
            console.log('heatmap:drawHeatmap (UTC Mode)');
        }

        let gutter = (settings.gutter !== undefined ? settings.gutter : '2px');
        if (typeof gutter === 'number') {
            gutter = `${gutter}px`;
        }
        const cellSize = settings.cellSize || 14;
        const cellSizePx = `${cellSize}px`;

        $el.empty();

        getData($el).then(rawData => {
            // Assuming rawData is [{ date: 'YYYY-MM-DD', count: N }, ...]
            const data = Array.isArray(rawData) ? rawData : (rawData ? JSON.parse(rawData) : []);
            if (!Array.isArray(data)) {
                throw new Error('Received data is not an array.');
            }

            if (settings.debug) {
                console.log('heatmap:drawHeatmap:data', data);
            }

            // Use moment instance only for locale-based month name formatting
            const monthFormatter = new Intl.DateTimeFormat(myMoment.locale(), { month: 'short', timeZone: 'UTC' });
            const firstDayOfWeek = 0; // Hardcoded Sunday start

            // --- Determine Start and End Dates (UTC) ---
            // Using today UTC as end date and 1 year before as start date
            const today = new Date();
            const todayUTCYear = today.getUTCFullYear();
            const todayUTCMonth = today.getUTCMonth();
            const todayUTCDate = today.getUTCDate();

            // End date is today (UTC)
            const endDateUTC = new Date(Date.UTC(todayUTCYear, todayUTCMonth, todayUTCDate));
            // Start date is 1 year before today (UTC)
            const startDateUTC = new Date(Date.UTC(todayUTCYear - 1, todayUTCMonth, todayUTCDate + 1)); // +1 to make it exactly 1 year inclusive? Check requirement. Often it's 365 days back. Let's stick to 1 year back for now.

            // Format as 'YYYY-MM-DD' strings
            const endDateStr = endDateUTC.toISOString().split('T')[0];
            const startDateStr = startDateUTC.toISOString().split('T')[0];

            if (settings.debug) {
                 console.log('DEBUG: Date Range (UTC):', { startDate: startDateStr, endDate: endDateStr });
            }
            // --- End Date Determination ---

            // Calculate weeks based on UTC start/end dates
            const weeks = calculateWeeks($el, startDateStr, endDateStr); // Uses UTC internally

            // Create a map using UTC 'YYYY-MM-DD' strings as keys
            const dataMap = new Map();
            for (let entry of data) {
                // Assuming entry.date is already 'YYYY-MM-DD' representing a UTC date
                if (entry.date && typeof entry.date === 'string') {
                     dataMap.set(entry.date, entry.count);
                } else if (settings.debug) {
                    console.warn('Skipping invalid data entry:', entry);
                }
            }

            const counts = data
                .map(entry => entry.count)
                .filter(count => typeof count === 'number' && count >= 0);

            const fallbackMin = 0;
            const fallbackMax = 1;
            const hasValidCounts = counts.length > 0;
            const minCount = hasValidCounts ? Math.min(...counts) : fallbackMin;
            const maxCount = hasValidCounts ? Math.max(...counts) : fallbackMax;

            if (settings.debug) {
                console.log('DEBUG: Min/Max Counts:', { minCount, maxCount, hasValidCounts });
            }

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

            // Prepare weeks data (map dates to counts)
            weeks.forEach(week => {
                week.forEach((utcDay, index) => {
                    // Get 'YYYY-MM-DD' string from the UTC date object
                    const dayKey = utcDay.toISOString().split('T')[0];
                    week[index] = {
                        date: utcDay, // Keep the UTC Date object
                        count: dataMap.get(dayKey) || 0,
                    };
                });
            });

            // --- Render Heatmap --- (No changes to structure/styling needed here)
            const heatmapContainer = $('<div class="heatmap-wrapper"></div>');
            heatmapContainer.css({
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'flex-start',
                gap: gutter,
            });

            const placeholder = $('<div class="month-placeholder"></div>');
            placeholder.css({
                height: cellSizePx,
                width: '100%', // Placeholder takes full width initially
                minWidth: `${cellSize * 1.5}px`, // Give labels some minimum space
                flexShrink: 0 // Prevent shrinking
            });


            const dayLabelColumn = $('<div class="day-labels"></div>');
            dayLabelColumn.append(placeholder.clone()); // Add placeholder at the top to align with month labels
            dayLabelColumn.css({
                display: 'grid',
                // gridTemplateRows: `repeat(8, ${cellSizePx})`, // 1 for placeholder + 7 for days
                gridTemplateRows: `${cellSizePx} repeat(7, ${cellSizePx})`, // Corrected: 1 placeholder, 7 days
                marginRight: gutter,
                textAlign: 'right', // Align text to the right if needed, center might be better
                rowGap: gutter,
                width: `${cellSize * 2}px`, // Estimate width for labels
                flexShrink: 0
            });

            // Generate day labels (Sun, Mon, ..., Sat) using locale from moment
            // Order is fixed: 0=Sun, 1=Mon, ... 6=Sat
            for (let dayIndex = 0; dayIndex < 7; dayIndex++) {
                 const tempDate = myMoment.clone().day(dayIndex); // Use moment just for day name formatting
                 const label = $('<div class="day-label"></div>');
                 label.text(tempDate.format('ddd')); // Get short day name (e.g., 'Sun', 'Mon')
                 label.css({
                     fontSize: `${cellSize * 0.7}px`,
                     color: '#ffffff', // Or desired color
                     textAlign: 'center',
                     lineHeight: cellSizePx,
                     height: cellSizePx,
                 });
                 dayLabelColumn.append(label);
            }

            heatmapContainer.append(dayLabelColumn);

            const heatmapGrid = $('<div class="heatmap"></div>');
            heatmapGrid.css({
                display: 'flex',
                gap: gutter,
                overflowX: 'auto' // Allow horizontal scrolling if needed
            });

            let lastRenderedMonth = -1;

            weeks.forEach(week => {
                const weekColumn = $('<div class="heatmap-week"></div>');
                weekColumn.css({
                    display: 'grid',
                    gridTemplateRows: `${cellSizePx} repeat(7, ${cellSizePx})`, // 1 for month label + 7 days
                    rowGap: gutter,
                });

                // Find the first day of the month in the current week (using UTC date)
                const firstDayOfMonthEntry = week.find(d => d.date && d.date.getUTCDate() === 1);
                const currentMonth = firstDayOfMonthEntry ? firstDayOfMonthEntry.date.getUTCMonth() : -1;

                if (currentMonth !== -1 && currentMonth !== lastRenderedMonth) {
                    lastRenderedMonth = currentMonth;
                    const monthLabel = $('<div class="month-label"></div>');
                    // Format month name using the UTC date and locale formatter
                    monthLabel.text(monthFormatter.format(firstDayOfMonthEntry.date));
                    monthLabel.css({
                        textAlign: 'left',
                        fontSize: `${cellSize * 0.7}px`,
                        lineHeight: cellSizePx,
                        height: cellSizePx,
                        width: cellSizePx, // Ensure it aligns with cells below
                        overflow: 'visible',
                        whiteSpace: 'nowrap'
                    });
                    weekColumn.append(monthLabel);
                } else {
                    // Add empty div to maintain grid structure
                    weekColumn.append('<div style="height: ' + cellSizePx + ';"></div>');
                }

                // Render day cells
                week.forEach(dayEntry => {
                    const cell = $('<div class="heatmap-cell"></div>');
                    // Compare with today's UTC date
                    const todayUTC = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate()));
                    const cellDateUTC = new Date(Date.UTC(dayEntry.date.getUTCFullYear(), dayEntry.date.getUTCMonth(), dayEntry.date.getUTCDate()));

                    cell.css({
                        width: cellSizePx,
                        height: cellSizePx,
                        backgroundColor: getCachedColor(dayEntry.count),
                        borderRadius: parseInt(gutter) > 2 ? '6px' : gutter,
                        cursor: 'pointer',
                        border: '1px solid rgba(255, 255, 255, 0.1)' // Default border
                    });

                    // Highlight today's cell (comparing UTC dates)
                    if (cellDateUTC.getTime() === todayUTC.getTime()) {
                        if (settings.debug) console.log(`Highlighting today (UTC): ${cellDateUTC.toISOString()}`);
                        cell.css("border", "1px solid rgb(207, 254, 216)"); // Highlight border
                    }

                    if (dayEntry.date) {
                        cell
                            .attr('data-bs-toggle', 'tooltip')
                            .attr('data-bs-custom-class', 'info-tooltip')
                            .attr('data-bs-html', true)
                            // Pass the UTC date object to the formatter
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
            // Initialize tooltips after adding elements to the DOM
            $el.find('[data-bs-toggle="tooltip"]').each(function() {
                new bootstrap.Tooltip(this);
            });
            $el.trigger('post.heatmap', [$el, data]); // Pass original structured data back
        }).catch(err => {
            console.error('Error loading or drawing heatmap data:', err);
            $el.append(`<div class="heatmap-error">${err.message || err}</div>`);
        }).finally(() => {
            // Final actions if needed
        });
    }


    function getContributionColor($el, count, minCount, maxCount) {
        const settings = getSettings($el);

        if (!settings.colors || Object.keys(settings.colors).length === 0) {
            settings.colors = $.heatmap.DEFAULTS.colors;
        }

        if (count === 0) {
            return settings.colors['0'];
        }

        const safeMin = Math.max(1, minCount);
        const safeCount = Math.max(1, count);
        const safeMax = Math.max(safeMin + 1, maxCount);

        const rangeLog = Math.log(safeMax) - Math.log(safeMin);
        let scaledPercentage = (Math.log(safeCount) - Math.log(safeMin)) / rangeLog;

        scaledPercentage = Math.pow(scaledPercentage, 1.5); // Ajuste exponencial

        scaledPercentage = Math.max(0, Math.min(scaledPercentage, 1));


        const colorKeys = Object.keys(settings.colors)
            .map(Number) 
            .sort((a, b) => a - b);


        let matchedKey = colorKeys.find(key => scaledPercentage <= key) || Math.max(...colorKeys);

        if (count !== 0 && count === minCount) {
            matchedKey = colorKeys.find(key => key > 0) || Math.max(...colorKeys);
        }

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

    
    // --- Plugin Definition ---
    $.fn.heatmap = function (options, params) {
        if ($(this).length > 1) {
            return $(this).each(function (i, element) {
                return $(element).heatmap(options, params);
            });
        }

        const $element = $(this);
        const methodCalled = typeof options === 'string';
        const isInitialized = $element.data('heatmapSettings');

        if (!isInitialized && !methodCalled) {
             // Initialize only if not already initialized and not calling a method
            init($element, options, true); // Pass true to draw immediately
        } else if (isInitialized && methodCalled) {
            // Handle method calls on an initialized element
            switch (options) {
                case 'updateOptions': {
                    const setup = $element.data('heatmapSettings');
                    if (setup.debug) {
                        console.log('heatmap:updateOptions (UTC Mode)', params);
                    }
                    // Merge new options with existing ones and defaults
                    const updatedSetup = $.extend({}, $.heatmap.DEFAULTS, setup, params || {});

                    // Update settings in data attribute
                    $element.data('heatmapSettings', updatedSetup);

                    // Re-create moment instance with potentially updated locale for formatting
                    const myMoment = moment().locale(updatedSetup.locale || $.heatmap.DEFAULTS.locale);

                    // Redraw the heatmap with updated settings
                    drawHeatmap($element, myMoment);
                    break;
                }
                 case 'getData': {
                     // Example method: return the fetched data (async)
                     // Note: This might need adjustment based on how you want to expose data
                     return getData($element); // Returns a Promise
                 }
                 case 'getSettings': {
                     return getSettings($element);
                 }
                // Add other methods here if needed
                default:
                    console.warn(`Heatmap method "${options}" not recognized.`);
            }
        } else if (!isInitialized && methodCalled) {
             console.error('Cannot call methods on an uninitialized heatmap.');
        }
        // Always return the jQuery object for chaining, unless a method returns a specific value (like getData promise or getSettings object)
        if (options !== 'getData' && options !== 'getSettings') {
             return $element;
        }
    }

}(jQuery));
