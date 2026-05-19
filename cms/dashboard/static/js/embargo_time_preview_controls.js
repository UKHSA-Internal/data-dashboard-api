// Embargo preview controls wired to the generic date-time picker launcher.

document.addEventListener('DOMContentLoaded', function () {
	let embargoTime = 'now';

	const embargoBtn = document.getElementById('embargo-time-btn-preview');
	const labelSpan = document.getElementById('embargo-time-btn-label');
	const previewBtn = document.querySelector('#preview-btn');

	const syncButton = () => {
		let display = 'now';
		if (embargoTime && embargoTime !== 'now') {
			const dt = new Date(Number(embargoTime) * 1000);
			display = new Intl.DateTimeFormat('en-GB', {
				weekday: 'short', day: '2-digit', month: 'short', year: 'numeric',
			}).format(dt);
		}
		if (embargoBtn) embargoBtn.title = `Set value: ${display}`;
		if (labelSpan) labelSpan.textContent = display;
	};

	syncButton();

	if (embargoBtn) {
		embargoBtn.addEventListener('click', async (e) => {
			e.preventDefault();
			const selectedValue = await globalThis.launchDateTimePicker?.({ defaultValue: embargoTime });
			if (selectedValue === null || selectedValue === undefined) {
				return;
			}
			embargoTime = selectedValue;
			syncButton();
		});
	}

	if (previewBtn) {
		previewBtn.addEventListener('click', (e) => {
			e.preventDefault();
			const baseUrl = previewBtn.dataset.url;
			if (!baseUrl) return;

			let url = baseUrl;
			const sep = url.includes('?') ? '&' : '?';
			url += sep + 'embargo_time=' + encodeURIComponent(embargoTime || 'now');
			window.open(url, '_blank', 'noopener');
		});
	}
});
