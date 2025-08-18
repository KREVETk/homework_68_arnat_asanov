document.addEventListener('DOMContentLoaded', () => {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

    async function toggleLike(type, id, btn, counterEl) {
        const liked = btn.classList.contains('liked');
        const url = `/api/${type}/${id}/`;
        const method = liked ? 'DELETE' : 'POST';

        try {
            const res = await fetch(url, {
                method: method,
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Accept': 'application/json',
                },
            });

            if (!res.ok) throw new Error('Ошибка запроса');
            const data = await res.json();

            counterEl.textContent = data.likes_count;
            btn.classList.toggle('liked', !liked);

        } catch (err) {
            console.error(err);
        }
    }

    document.querySelectorAll('.like-btn').forEach(btn => {
        const type = btn.dataset.type;  // "article" или "comment"
        const id = btn.dataset.id;
        const counterEl = btn.nextElementSibling;

        btn.addEventListener('click', () => toggleLike(type, id, btn, counterEl));
    });
});
