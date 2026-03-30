// embargo_time_picker.js
// Shared embargo time picker logic for Preview and View Live buttons using flatpickr

document.addEventListener('DOMContentLoaded', function () {
    // In-memory embargo time state
    // Default state is the literal string "now".
    let embargoTime = 'now';

    const formatDisplayValue = (value) => {
        if (!value || value === 'now') {
            return 'now';
        }

        const epochSeconds = Number(value);
        if (!Number.isFinite(epochSeconds)) {
            return String(value);
        }

        const dt = new Date(epochSeconds * 1000);
        return new Intl.DateTimeFormat('en-GB', {
            weekday: 'long',
            day: '2-digit',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            timeZoneName: 'short',
        }).format(dt);
    };

    const updateEmbargoButtonDisplay = (embargoBtn, labelSpan) => {
        const displayValue = formatDisplayValue(embargoTime);
        if (embargoBtn) {
            embargoBtn.title = embargoTime ? `Set value: ${displayValue}` : 'No embargo time set';
        }
        if (labelSpan) {
            labelSpan.textContent = displayValue;
        }
    };

    // Set initial label
    const initialEmbargoBtn = document.getElementById('embargo-time-btn-preview');
    const initialLabelSpan = document.getElementById('embargo-time-btn-label');
    updateEmbargoButtonDisplay(initialEmbargoBtn, initialLabelSpan);

    // Create modal HTML if not present
    if (!document.getElementById('embargo-time-modal')) {
        const modal = document.createElement('div');
        modal.id = 'embargo-time-modal';
        modal.style.display = 'none';
        modal.innerHTML = `
            <div class="embargo-modal-content">
                <label for="embargo-time-input" style="display:none;">Select embargo time:</label>
                <input id="embargo-time-input" type="text" style="display:none;" />
                <div id="embargo-calendar-container"></div>
                <a id="embargo-ok-btn" href="#" class="button embargo-modal-btn">OK</a>
                <a id="embargo-cancel-btn" href="#" class="button button-secondary embargo-modal-btn">Cancel</a>
            </div>
            <style>
                #embargo-time-modal { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.3); z-index: 9999; display: flex; align-items: center; justify-content: center; }
                .embargo-modal-content { background: #fff; padding: 2em; border-radius: 8px; box-shadow: 0 2px 16px rgba(0,0,0,0.2); min-width: 300px; }
                .embargo-modal-content .embargo-modal-btn { margin: 0.5em 0.5em 0 0; font-size: 0.85em; padding: 0.3em 1.1em; height: 2.1em; line-height: 1.2; min-width: 0; }
                .embargo-modal-content .icon { height: 1em; width: 1em; vertical-align: middle; }
                /* Fix flatpickr header clipping and reduce size */
                .flatpickr-calendar .flatpickr-months { font-size: 0.95em; min-height: 28px; }
                .flatpickr-calendar .flatpickr-month { padding: 2px 0 2px 0; }
                .flatpickr-calendar .flatpickr-current-month { font-size: 0.95em; padding: 0 2px; }
                .flatpickr-calendar .flatpickr-monthDropdown-months { font-size: 0.95em; padding: 0 2px; }
                .flatpickr-calendar .numInput.cur-year { font-size: 0.95em; width: 3.5em; }
                .flatpickr-calendar .arrowUp, .flatpickr-calendar .arrowDown { height: 0.7em; }
                .flatpickr-calendar .flatpickr-prev-month, .flatpickr-calendar .flatpickr-next-month { font-size: 1em; padding: 0 4px; }
                .flatpickr-calendar .flatpickr-months { overflow: visible !important; }
            </style>
        `;
        document.body.appendChild(modal);
    }

    // Initialize flatpickr
    let embargoPicker = null;

    const buildDateFromPicker = (instance) => {
        const fallback = new Date();
        const base = instance.selectedDates[0] || fallback;
        const year = Number(instance.currentYear);
        const month = Number(instance.currentMonth);
        const day = Number(base.getDate());
        const hours = instance.hourElement ? Number(instance.hourElement.value) : base.getHours();
        const minutes = instance.minuteElement ? Number(instance.minuteElement.value) : base.getMinutes();
        return new Date(year, month, day, hours, minutes, 0, 0);
    };

    function showEmbargoModal(callback) {
        const modal = document.getElementById('embargo-time-modal');
        modal.style.display = 'flex';
        const calendarContainer = document.getElementById('embargo-calendar-container');
        // Remove any previous calendar
        calendarContainer.innerHTML = '';
        const calendarInput = document.createElement('input');
        calendarInput.type = 'text';
        calendarInput.style.display = 'none';
        calendarContainer.appendChild(calendarInput);
        embargoPicker = flatpickr(calendarInput, {
            enableTime: true,
            dateFormat: 'Y-m-d H:i',
            defaultDate: embargoTime === 'now' ? new Date() : new Date(Number(embargoTime) * 1000),
            allowInput: false,
            inline: true,
            onReady: function(selectedDates, dateStr, instance) {
                // Ensure there is always a selected datetime when modal opens.
                instance.setDate(embargoTime === 'now' ? new Date() : new Date(Number(embargoTime) * 1000), true);
            }
        });
        // OK button
        document.getElementById('embargo-ok-btn').onclick = function () {
            // Commit the datetime represented by current picker state.
            const selectedDate = buildDateFromPicker(embargoPicker);
            embargoTime = Math.floor(selectedDate.getTime() / 1000).toString();
            modal.style.display = 'none';
            // Set alt text (title) and label on the button
            const embargoBtn = document.getElementById('embargo-time-btn-preview');
            const labelSpan = document.getElementById('embargo-time-btn-label');
            updateEmbargoButtonDisplay(embargoBtn, labelSpan);
            callback(embargoTime);
        };
        // Cancel button
        document.getElementById('embargo-cancel-btn').onclick = function () {
            modal.style.display = 'none';
        };
    }

    // Attach to all embargo time buttons
    function attachEmbargoLogic(buttonSelector, actionButtonSelector, urlAttr) {
        const embargoBtn = document.querySelector(buttonSelector);
        const actionBtn = document.querySelector(actionButtonSelector);
        if (!embargoBtn || !actionBtn) return;
        embargoBtn.addEventListener('click', function (e) {
            e.preventDefault();
            showEmbargoModal(function (selected) {
                // embargoTime is already set in showEmbargoModal
                const labelSpan = document.getElementById('embargo-time-btn-label');
                updateEmbargoButtonDisplay(embargoBtn, labelSpan);
            });
        });
        actionBtn.addEventListener('click', function (e) {
            // Always use the current embargoTime (default to literal "now" if not set)
            let timeToUse = embargoTime;
            if (!timeToUse) {
                timeToUse = 'now';
                embargoTime = timeToUse;
            }
            let url = actionBtn.getAttribute(urlAttr);
            const sep = url.includes('?') ? '&' : '?';
            url += sep + 'embargo_time=' + encodeURIComponent(timeToUse);
            window.open(url, '_blank', 'noopener');
            e.preventDefault();
        });
    }

    // Example usage: update selectors as needed for your template
    attachEmbargoLogic('#embargo-time-btn-preview', '#preview-btn', 'data-url');
});
