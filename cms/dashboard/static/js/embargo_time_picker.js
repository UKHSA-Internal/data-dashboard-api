// embargo_time_picker.js
// Shared embargo time picker logic for Preview and View Live buttons using flatpickr

document.addEventListener('DOMContentLoaded', function () {
    // In-memory embargo time state
    let embargoTime = null;

    // Create modal HTML if not present
    if (!document.getElementById('embargo-time-modal')) {
        const modal = document.createElement('div');
        modal.id = 'embargo-time-modal';
        modal.style.display = 'none';
        modal.innerHTML = `
            <div class="embargo-modal-content">
                <label for="embargo-time-input">Select embargo time:</label>
                <input id="embargo-time-input" type="text" />
                <a id="embargo-now-btn" href="#" class="button button-secondary embargo-modal-btn">Set to Now</a>
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
    function showEmbargoModal(callback) {
        const modal = document.getElementById('embargo-time-modal');
        const input = document.getElementById('embargo-time-input');
        modal.style.display = 'flex';
        if (!embargoPicker) {
            embargoPicker = flatpickr(input, {
                enableTime: true,
                dateFormat: 'Y-m-d H:i',
                defaultDate: embargoTime ? embargoTime : new Date(),
                allowInput: true,
                onReady: function(selectedDates, dateStr, instance) {
                    // Only add once
                    if (!instance.calendarContainer.querySelector('.flatpickr-ok-btn')) {
                        const okBtn = document.createElement('button');
                        okBtn.type = 'button';
                        okBtn.textContent = 'OK';
                        okBtn.className = 'button button-small flatpickr-ok-btn';
                        okBtn.style.margin = '8px auto 4px auto';
                        okBtn.style.display = 'block';
                        okBtn.onclick = function() {
                            // Set the input value to the selected date/time
                            if (instance.selectedDates.length > 0) {
                                const formatted = instance.formatDate(instance.selectedDates[0], instance.config.dateFormat);
                                input.value = formatted;
                                embargoTime = formatted;
                            }
                            instance.close();
                        };
                        instance.calendarContainer.appendChild(okBtn);
                    }
                }
            });
        } else {
            embargoPicker.setDate(embargoTime ? embargoTime : new Date());
        }
        // Set to now button
        document.getElementById('embargo-now-btn').onclick = function () {
            embargoPicker.setDate(new Date());
        };
        // OK button
        document.getElementById('embargo-ok-btn').onclick = function () {
            embargoTime = input.value;
            modal.style.display = 'none';
            callback(input.value);
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
            });
        });
        actionBtn.addEventListener('click', function (e) {
            // Always use the current embargoTime (may be null)
            if (embargoTime) {
                let url = actionBtn.getAttribute(urlAttr);
                const sep = url.includes('?') ? '&' : '?';
                url += sep + 'embargo_now=' + encodeURIComponent(embargoTime);
                window.location.href = url;
                e.preventDefault();
            }
        });
    }

    // Example usage: update selectors as needed for your template
    attachEmbargoLogic('#embargo-time-btn-preview', '#preview-btn', 'data-url');
    attachEmbargoLogic('#embargo-time-btn-viewlive', '#viewlive-btn', 'data-url');
    attachEmbargoLogic('#embargo-time-btn-viewlive-modal', '#viewlive-btn-modal', 'data-url');
});
