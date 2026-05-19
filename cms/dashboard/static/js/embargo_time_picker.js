// Generic date picker launcher used by the embargo preview controls.

const createDateTimePickerLauncher = ({
    modal,
    calendarContainer,
    okBtn,
    nowBtn,
    cancelBtn,
} = {}) => {
    if (!modal || !calendarContainer || !okBtn || !nowBtn || !cancelBtn) {
        return async () => null;
    }

    let previouslyFocusedElement = null;

    const openModal = () => {
        if (!modal) {
            return;
        }

        if (typeof modal.showModal === 'function') {
            modal.showModal();
            return;
        }

        modal.setAttribute('open', 'open');
    };

    const closeModal = () => {
        if (modal) {
            if (typeof modal.close === 'function' && modal.open) {
                modal.close();
            } else {
                modal.removeAttribute('open');
            }
        }
        // Restore focus to the element that opened the modal
        if (previouslyFocusedElement) {
            previouslyFocusedElement.focus();
            previouslyFocusedElement = null;
        }
    };

    const setOkButtonEnabled = (isEnabled) => {
        if (!okBtn) return;
        okBtn.disabled = !isEnabled;
    };

    const setupYearControls = (instance) => {
        const calendar = instance.calendarContainer;
        const monthsContainer = calendar.querySelector('.flatpickr-months');
        const innerContainer = calendar.querySelector('.flatpickr-innerContainer');
        if (!monthsContainer || !innerContainer) return;

        monthsContainer.classList.add('embargo-native-header-hidden');

        let navRow = calendar.querySelector('.embargo-custom-nav');
        if (!navRow) {
            navRow = document.createElement('div');
            navRow.className = 'embargo-custom-nav';
            innerContainer.before(navRow);
        }

        const monthName = instance.l10n?.months?.longhand?.[instance.currentMonth] || '';
        const yearNumber = Number.isInteger(instance.currentYear) ? String(instance.currentYear) : '';
        const monthYearLabel = `${monthName} ${yearNumber}`.trim() || 'Month Year';
        navRow.innerHTML = '';

        const leftControls = document.createElement('div');
        leftControls.className = 'embargo-custom-nav-group';
        const rightControls = document.createElement('div');
        rightControls.className = 'embargo-custom-nav-group';
        rightControls.classList.add('embargo-custom-nav-group-end');

        const monthDisplay = document.createElement('div');
        monthDisplay.className = 'embargo-nav-label';
        monthDisplay.textContent = monthYearLabel;

        const prevYearBtn = document.createElement('button');
        prevYearBtn.type = 'button';
        prevYearBtn.className = 'embargo-nav-btn';
        prevYearBtn.textContent = '<<';
        prevYearBtn.title = 'Previous year';
        prevYearBtn.setAttribute('aria-label', 'Previous year');
        prevYearBtn.onclick = (e) => {
            e.preventDefault();
            instance.changeYear(instance.currentYear - 1);
            setupYearControls(instance);
        };

        const prevMonthBtn = document.createElement('button');
        prevMonthBtn.type = 'button';
        prevMonthBtn.className = 'embargo-nav-btn';
        prevMonthBtn.textContent = '<';
        prevMonthBtn.title = 'Previous month';
        prevMonthBtn.setAttribute('aria-label', 'Previous month');
        prevMonthBtn.onclick = (e) => {
            e.preventDefault();
            instance.changeMonth(-1);
            setupYearControls(instance);
        };

        const nextMonthBtn = document.createElement('button');
        nextMonthBtn.type = 'button';
        nextMonthBtn.className = 'embargo-nav-btn';
        nextMonthBtn.textContent = '>';
        nextMonthBtn.title = 'Next month';
        nextMonthBtn.setAttribute('aria-label', 'Next month');
        nextMonthBtn.onclick = (e) => {
            e.preventDefault();
            instance.changeMonth(1);
            setupYearControls(instance);
        };

        const nextYearBtn = document.createElement('button');
        nextYearBtn.type = 'button';
        nextYearBtn.className = 'embargo-nav-btn';
        nextYearBtn.textContent = '>>';
        nextYearBtn.title = 'Next year';
        nextYearBtn.setAttribute('aria-label', 'Next year');
        nextYearBtn.onclick = (e) => {
            e.preventDefault();
            instance.changeYear(instance.currentYear + 1);
            setupYearControls(instance);
        };

        leftControls.appendChild(prevYearBtn);
        leftControls.appendChild(prevMonthBtn);
        rightControls.appendChild(nextMonthBtn);
        rightControls.appendChild(nextYearBtn);

        navRow.appendChild(leftControls);
        navRow.appendChild(monthDisplay);
        navRow.appendChild(rightControls);
    };

    return ({ defaultValue = 'now' } = {}) => new Promise((resolve) => {
        previouslyFocusedElement = document.activeElement;
        calendarContainer.innerHTML = '';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'embargo-picker-input';
        calendarContainer.appendChild(input);

        const parsedDefaultDate = defaultValue === 'now'
            ? new Date()
            : new Date(Number(defaultValue) * 1000);

        let picker = null;
        let isResolved = false;

        const cleanup = () => {
            okBtn.removeEventListener('click', onOk);
            nowBtn.removeEventListener('click', onNow);
            cancelBtn.removeEventListener('click', onCancel);
            modal.removeEventListener('cancel', onModalCancel);
            document.removeEventListener('keydown', onKeyDown);
            if (picker) {
                picker.destroy();
            }
            calendarContainer.innerHTML = '';
        };

        const finish = (value) => {
            if (isResolved) return;
            isResolved = true;
            cleanup();
            closeModal();
            resolve(value);
        };

        const onOk = (e) => {
            e.preventDefault();
            const selected = picker?.selectedDates?.[0];
            if (!selected) return;

            const midnight = new Date(selected.getFullYear(), selected.getMonth(), selected.getDate());
            finish(Math.floor(midnight.getTime() / 1000).toString());
        };

        const onNow = (e) => {
            e.preventDefault();
            finish('now');
        };

        const onCancel = (e) => {
            e.preventDefault();
            finish(null);
        };

        const onModalCancel = (e) => {
            e.preventDefault();
            finish(null);
        };

        const onKeyDown = (e) => {
            if (e.key === 'Escape' && modal.open) {
                e.preventDefault();
                finish(null);
            }
        };

        okBtn.addEventListener('click', onOk);
        nowBtn.addEventListener('click', onNow);
        cancelBtn.addEventListener('click', onCancel);
        modal.addEventListener('cancel', onModalCancel);
        document.addEventListener('keydown', onKeyDown);

        picker = flatpickr(input, {
            dateFormat: 'Y-m-d',
            defaultDate: parsedDefaultDate,
            inline: true,
            monthSelectorType: 'static',
            onReady: (_selectedDates, _dateStr, instance) => {
                // Require an explicit day click each time the modal opens.
                instance.clear();
                setOkButtonEnabled(false);
                setupYearControls(instance);
            },
            onChange: (selectedDates) => {
                setOkButtonEnabled(selectedDates.length > 0);
            },
            onMonthChange: (_selectedDates, _dateStr, instance) => {
                setupYearControls(instance);
            },
            onYearChange: (_selectedDates, _dateStr, instance) => {
                setupYearControls(instance);
            },
        });

        openModal();
        // Move focus to OK button (or first focusable element in modal)
        setTimeout(() => {
            const firstFocusableElement = modal.querySelector('button');
            if (firstFocusableElement) {
                firstFocusableElement.focus();
            }
        }, 0);
    });
};

document.addEventListener('DOMContentLoaded', function () {
    globalThis.launchDateTimePicker = createDateTimePickerLauncher({
        modal: document.getElementById('embargo-time-modal'),
        calendarContainer: document.getElementById('embargo-calendar-container'),
        okBtn: document.getElementById('embargo-ok-btn'),
        nowBtn: document.getElementById('embargo-now-btn'),
        cancelBtn: document.getElementById('embargo-cancel-btn'),
    });
});

