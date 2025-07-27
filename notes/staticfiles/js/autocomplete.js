document.addEventListener('DOMContentLoaded', function () {
    const searchInput = document.getElementById('searchInput');
    const suggestionsBox = document.getElementById('suggestions');

    searchInput.addEventListener('input', function () {
        const query = this.value;
        if (query.length < 2) {
            suggestionsBox.style.display = 'none';
            return;
        }
        fetch(`/autocomplete/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                suggestionsBox.innerHTML = '';
                if (data.results.length > 0) {
                    data.results.forEach(item => {
                        const div = document.createElement('div');
                        div.textContent = item;
                        div.style.padding = '5px';
                        div.style.cursor = 'pointer';
                        div.addEventListener('click', function () {
                            searchInput.value = this.textContent;
                            suggestionsBox.style.display = 'none';
                            document.getElementById('filterForm').submit();
                        });
                        suggestionsBox.appendChild(div);
                    });
                    suggestionsBox.style.display = 'block';
                } else {
                    suggestionsBox.style.display = 'none';
                }
            })
            .catch(() => {
                suggestionsBox.style.display = 'none';
            });
    });

    document.addEventListener('click', function (e) {
        if (e.target !== searchInput) {
            suggestionsBox.style.display = 'none';
        }
    });
});
