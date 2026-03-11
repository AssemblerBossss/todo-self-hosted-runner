/**
 * Обновление access токена через refresh токен (из httpOnly cookie)
 */
async function refreshAccessToken() {
    try {
        const response = await fetch('/auth/refresh', {
            method: 'POST',
            credentials: 'same-origin'
        });

        if (!response.ok) {
            throw new Error('Failed to refresh token');
        }

        return true; // куки обновились на сервере, этого достаточно
    } catch (error) {
        console.error('Token refresh failed:', error);
        window.location.href = '/auth/login';
        return false;
    }
}

/**
 * fetch с автоматическим обновлением токена при 401.
 * Используй вместо обычного fetch() везде, где нужна авторизация.
 */
async function fetchWithAuth(url, options = {}) {
    let response = await fetch(url, {
        ...options,
        credentials: 'same-origin'
    });

    if (response.status === 401) {
        const refreshed = await refreshAccessToken();

        if (refreshed) {
            // Повторяем оригинальный запрос с обновлёнными куками
            response = await fetch(url, {
                ...options,
                credentials: 'same-origin'
            });
        }
    }

    return response;
}